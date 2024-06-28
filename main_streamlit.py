import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from pre_processing import *
from database import *
from PIL import Image
import pytesseract
import pdfplumber
import os

st.set_page_config(page_title="My Streamlit App", page_icon="❓")
st.title("PDF/Text Question Generator")

st.markdown("""Welcome to the PDF/Text Question Generator! This tool allows you to upload a PDF file or input text directly to generate detailed questions.""")

st.sidebar.header("Available Model Options")
m = st.sidebar.selectbox("Select the model", ("Gemini", "Claude", "OpenAI ChatGPT"))

st.sidebar.header("User Input Options")
input_type = st.sidebar.radio("Select input type", ("PDF File", "Text Input"))

model = model_selection(m)

st.write(f"Currently Using Model : {m}")

if 'buffer' not in st.session_state:
    clear_data()
    st.session_state.buffer = True

if 'uploaded_pdf' not in st.session_state:
    st.session_state.uploaded_pdf = None

if 'accepted_questions' not in st.session_state:
    st.session_state.accepted_questions = []

if input_type == "PDF File":
    pdf_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])
    language = st.sidebar.selectbox("Select Language of the PDF", ("English", "Hindi"))
else:
    text_input = st.sidebar.text_area("Enter your text")
    language = st.sidebar.selectbox("Select Language of the PDF", ("English", "Hindi"))

prompt = st.sidebar.text_area("Enter your prompt for generating questions", height=100)
question_type = st.sidebar.selectbox("Select type of questions to generate", ("Descriptive", "MCQ", "Fill in the Blanks"))
question_level = st.sidebar.selectbox("Select Level of the Questions", ("Easy", "Medium", "Hard"))
bloom = st.sidebar.selectbox("Select Bloom's Taxonomy Level", ("Knowledge", "Comprehension", "Application", "Analysis", "Synthesis", "Evaluation"))

num_questions = st.sidebar.number_input("Number of questions to generate", min_value=1, max_value=20, value=10)

generate_questions_flag = st.sidebar.button("Generate Questions")
json_object = None

def ocr_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            image = page.to_image()
            page_text = pytesseract.image_to_string(image.original, lang='hin')
            text += page_text + "\n\n"
    return text

if generate_questions_flag:
    if input_type == "PDF File":
        if pdf_file != st.session_state.uploaded_pdf:
            with st.spinner("Extracting text and images from PDF..."):
                if language == "Hindi":
                    combined_text = ocr_from_pdf(pdf_file)
                else:
                    combined_text = handle_pdf_file(pdf_file, model, m)
                save_data_to_db(combined_text)
            st.session_state.uploaded_pdf = pdf_file
        combined_text = get_data()
        if combined_text:
            with st.spinner("Generating questions..."):
                questions = generate_questions(model, m, combined_text, prompt, question_type, question_level, bloom, language, num_questions)
        else:
            st.write("No data available. Upload File again")
        st.success("Questions generated successfully!")
        save_questions_to_db(questions, question_type, bloom)

    elif input_type == "Text Input" and text_input:
        combined_text = text_input
        save_data_to_db(combined_text)
        combined_text = get_data()
        if combined_text:
            with st.spinner("Generating questions..."):
                questions = generate_questions(model, m, combined_text, prompt, question_type, question_level, bloom, language, num_questions)
        else:
            st.write("No data available. Upload File again")
        
        st.success("Questions generated successfully!")
        save_questions_to_db(questions, question_type, bloom)
    else:
        st.error("Please upload a PDF file or enter text, and enter a prompt.")
        combined_text = None

st.markdown("### Generated Questions")
all_questions = get_all_questions()
for i, question in enumerate(all_questions, 1):
    st.write(f"*Question {i}*")
    st.write(question["Question"])
    if question["question_type"] == "MCQ":
        st.write("*Options*")
        for option in question["Options"]:
            st.write(option)
    st.write("*Answer*")
    st.write(question["Answer"])
    
    if st.button(f"Accept Question {i}"):
        if question not in st.session_state.accepted_questions:
            st.session_state.accepted_questions.append(question)
            st.success(f"Question {i} accepted!")
        else:
            st.warning(f"Question {i} already accepted.")

if st.button("Send Accepted Questions to API"):
    if st.session_state.accepted_questions:
        with st.spinner("Sending accepted questions to API..."):
            for question in st.session_state.accepted_questions:
                response, status = send_insomnia_request(question)
                st.write(f"Question sent to API. Response: {response}, Status: {status}")
        st.success("All accepted questions sent to API!")
        st.session_state.accepted_questions = []  # Clear accepted questions after sending
    else:
        st.warning("No questions have been accepted yet.")

st.sidebar.markdown("<h2>PDF Splitter</h2>", unsafe_allow_html=True)
split_pdf_file = st.sidebar.file_uploader("Upload a PDF file for splitting", type=["pdf"])
page_ranges = st.sidebar.text_input("Enter page ranges (e.g., 1-3, 4-5)")
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