from pymongo import MongoClient
import os
import base64
from PyPDF2 import PdfReader
import google.generativeai as genai
from database import save_questions_to_db, get_all_questions
import streamlit as st

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
    text = ""
    images = []
    with open(pdf_path, "rb") as file:
        pdf_reader = PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
            if "/XObject" in page["/Resources"]:
                xObject = page["/Resources"]["/XObject"].get_object()
                for obj in xObject:
                    if xObject[obj]["/Subtype"] == "/Image":
                        images.append(xObject[obj].get_data())
    return text, images

def preprocess_images(images):
    image_descriptions = []
    for image_bytes in images:
        try:
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            image_path = "temp_image.jpg"
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
        except Exception as e:
            st.error(f"Error processing image: {e}")
            continue
    return image_descriptions

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

st.sidebar.header("User Input Options")
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
    num_images = len(images)
    st.write(f"Number of images extracted: {num_images}")
    if num_images > 25 and not st.session_state.proceed_with_text_only:
        st.session_state.too_many_images = True
        st.experimental_rerun()
    else:
        st.session_state.too_many_images = False
        if st.session_state.proceed_with_text_only:
            combined_text = text
        else:
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

if "too_many_images" in st.session_state and st.session_state.too_many_images:
    st.error("Too many images detected! More than 25 images found.")
    if st.sidebar.button("Proceed with Text Only"):
        st.session_state.proceed_with_text_only = True
        st.experimental_rerun()

if st.sidebar.button("Show All Questions"):
    all_questions = get_all_questions()
    st.markdown("### All Stored Questions")
    for question in all_questions:
        st.write(question["text"])


st.markdown("---")
st.markdown("2024 PDF/Text Question Generator/YMG")
