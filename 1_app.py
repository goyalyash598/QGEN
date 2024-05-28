import streamlit as st
from pymongo import MongoClient
import os
import base64
import google.generativeai as genai
from database import save_questions_to_db, get_all_questions
import io
import fitz
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

st.set_page_config(page_title="PDF/Text Question Generator", layout="wide")

mongo_connection_string = st.secrets["mongo"]["connection_string"]
api_key = st.secrets["api_keys"]["genai_api_key"]

client = MongoClient(mongo_connection_string)
db = client.questions_db
questions_collection = db.questions

genai.configure(api_key=api_key)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file

def extract_text_and_images(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = ""
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            images.append(image_data)
        extracted_text += text.strip()
    return extracted_text, images

def preprocess_images(images):
    image_descriptions = []
    image_merge = []
    for image_bytes in images:
        try:
            image_stream = io.BytesIO(image_bytes)
            image = Image.open(image_stream)
            image_merge.append(image)
        except Exception as e:
            with open("Error logs(bytes).txt", "w") as f:
                f.write(str(e))
    step = 5
    for i in range(0, len(image_merge), step):
        combined_image = combine_images(image_merge[i:i+step])
        image_path = "temp_image.jpg"
        try:
            buffer = io.BytesIO()
            combined_image.save(buffer, format="JPEG")
        except Exception as e:
            with open("Error logs(Buffer).txt", "w") as f:
                f.write(str(e))
        while True:
            try:
                image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                buffer.close()
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(image_base64))
                image_file = upload_to_gemini(image_path)
                chat_session = model.start_chat(
                    history=[
                        {"role": "user", "parts": ["from my local image path, summarize the given image", image_file]},
                        {"role": "model", "parts": ["Your description of the image goes here."]},
                    ]
                )
                response = chat_session.send_message("Describe the image in more detail.")
                image_descriptions.append(response.text)
                os.remove(image_path)
                break
            except Exception as e:
                st.write(f"Error processing image: {e}")
                continue
    return image_descriptions

def combine_images(images, mode='vertical'):
    if not images:
        return None

    if mode == 'vertical':
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images)
        combined_image = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for img in images:
            combined_image.paste(img, (0, y_offset))
            y_offset += img.height

    elif mode == 'horizontal':
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)
        combined_image = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for img in images:
            combined_image.paste(img, (x_offset, 0))
            x_offset += img.width

    elif mode == 'grid':
        cols = 2
        rows = (len(images) + 1) // cols
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        combined_image = Image.new('RGB', (cols * max_width, rows * max_height))

        for idx, img in enumerate(images):
            x_offset = (idx % cols) * max_width
            y_offset = (idx // cols) * max_height
            combined_image.paste(img, (x_offset, y_offset))

    return combined_image

def generate_questions(combined_text, prompt, question_type, num_questions=10):
    if question_type == "Descriptive":
        user_prompt = f"{prompt}\n\nBased on the following text, generate {num_questions} detailed descriptive questions only:\n\n{combined_text}"
    elif question_type == "MCQ":
        user_prompt = f"{prompt}\n\nBased on the following text, generate {num_questions} multiple-choice questions (MCQs) with four options each:\n\n{combined_text}"
    elif question_type == "Fill in the Blanks":
        user_prompt = f"{prompt}\n\nBased on the following text, generate {num_questions} fill-in-the-blank questions only:\n\n{combined_text}"

    try:
        chat_session = model.start_chat(history=[{"role": "user", "parts": [user_prompt]}])
        response = chat_session.send_message(f"Please provide {num_questions} questions as requested, without any additional context.")
        questions = response.text.split("\n")
        filtered_questions = [question.strip() for question in questions if question.strip()]
        return filtered_questions[:num_questions]
    except Exception as e:
        st.error(f"Error generating questions: {e}")
        return []

st.title("PDF/Text Question Generator")

st.markdown("""Welcome to the PDF/Text Question Generator! This tool allows you to upload a PDF file or input text directly to generate detailed questions.""")

st.sidebar.markdown("<h2>User Input Options</h2>", unsafe_allow_html=True)
input_type = st.sidebar.radio("Select input type", ("PDF File", "Text Input"))

if input_type == "PDF File":
    pdf_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])
else:
    text_input = st.sidebar.text_area("Enter your text")

prompt = st.sidebar.text_area("Enter your prompt for generating questions", height=100)
question_type = st.sidebar.selectbox("Select type of questions to generate", ("Descriptive", "MCQ", "Fill in the Blanks"))
num_questions = st.sidebar.number_input("Number of questions to generate", min_value=1, max_value=20, value=10)

if "proceed_with_text_only" not in st.session_state:
    st.session_state.proceed_with_text_only = False

generate_questions_flag = st.sidebar.button("Generate Questions")

def handle_pdf_file(pdf_file):
    pdf_path = f"temp_{pdf_file.name}"
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getbuffer())
    text, images = extract_text_and_images(pdf_path)
    st.write(f"Number of images extracted: {len(images)}")
    image_descriptions = preprocess_images(images)
    combined_text = text + " ".join(image_descriptions)
    os.remove(pdf_path)
    return combined_text

if generate_questions_flag or st.session_state.proceed_with_text_only:
    if input_type == "PDF File" and pdf_file:
        with st.spinner("Extracting text and images from PDF..."):
            combined_text = handle_pdf_file(pdf_file)
    elif input_type == "Text Input" and text_input:
        combined_text = text_input
    else:
        st.error("Please upload a PDF file or enter text, and enter a prompt.")
        combined_text = None

    if combined_text:
        with st.spinner("Generating questions..."):
            questions = generate_questions(combined_text, prompt, question_type, num_questions)

        st.success("Questions generated successfully!")
        st.markdown("### Generated Questions")
        for question in questions:
            st.write(question)

        save_questions_to_db(questions)
        st.session_state.proceed_with_text_only = False

if st.sidebar.button("Show All Questions"):
    all_questions = get_all_questions()
    st.markdown("### All Stored Questions")
    for question in all_questions:
        st.write(question["text"])

# Separator line
st.sidebar.markdown("<hr style='border:1px solid black'>", unsafe_allow_html=True)

# PDF Splitter functionality
st.sidebar.markdown("<h2>PDF Splitter</h2>", unsafe_allow_html=True)
split_pdf_file = st.sidebar.file_uploader("Upload a PDF to split", type=["pdf"])
page_ranges = st.sidebar.text_input("Enter page ranges (e.g., 11-33, 40-55)")
split_button = st.sidebar.button("Split PDF")

def split_pdf(input_pdf, output_folder, page_range):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(input_pdf, 'rb') as infile:
        reader = PdfReader(infile)
        for start, end in page_range:
            writer = PdfWriter()
            for page_number in range(start - 1, end):
                writer.add_page(reader.pages[page_number])
            output_pdf = os.path.join(output_folder, f'pages_{start}_{end}.pdf')
            with open(output_pdf, 'wb') as outfile:
                writer.write(outfile)
            print(f'Saved pages {start} to {end} as {output_pdf}')
            st.write(f"Saved pages {start} to {end} as {output_pdf}")

if split_button and split_pdf_file and page_ranges:
    try:
        pdf_path = f"split_temp_{split_pdf_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(split_pdf_file.getbuffer())

        output_folder = 'output_folder'
        page_range = [(int(range_str.split('-')[0]), int(range_str.split('-')[1])) for range_str in page_ranges.split(',')]
        split_pdf(pdf_path, output_folder, page_range)

        st.success("PDF split successfully!")
        for start, end in page_range:
            output_pdf = os.path.join(output_folder, f'pages_{start}_{end}.pdf')
            with open(output_pdf, "rb") as file:
                st.download_button(label=f"Download pages {start}-{end}", data=file, file_name=f'pages_{start}_{end}.pdf')

        os.remove(pdf_path)
    except Exception as e:
        st.error(f"Error splitting PDF: {e}")

st.markdown("---")
st.markdown("2024 PDF/Text Question Generator/YMG")
