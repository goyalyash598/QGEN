from PyPDF2 import PdfReader, PdfWriter
import streamlit as st
from pre_processing import *
from database import *

st.set_page_config(page_title="PDF/Text Question Generator", layout="wide", page_icon="❓")
st.title("📄 PDF/Text Question Generator")
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

if input_type == "PDF File":
    pdf_file = st.sidebar.file_uploader("Upload a PDF file", type=["pdf"])
    
else:
    text_input = st.sidebar.text_area("Enter your text")

prompt = st.sidebar.text_area("Enter your prompt for generating questions", height=100)
question_type = st.sidebar.selectbox("Select type of questions to generate", ("Descriptive", "MCQ", "Fill in the Blanks"))
num_questions = st.sidebar.number_input("Number of questions to generate", min_value=1, max_value=20, value=10)

generate_questions_flag = st.sidebar.button("Generate Questions")
json_object = None

if generate_questions_flag:
 
    if input_type == "PDF File" :

            if pdf_file != st.session_state.uploaded_pdf:
                with st.spinner("Extracting text and images from PDF..."):
                    combined_text = handle_pdf_file(pdf_file,model,m)
                    save_data_to_db(combined_text)
                st.session_state.uploaded_pdf = pdf_file
            combined_text = get_data()
            if combined_text:
                    with st.spinner("Generating questions..."):
                        questions = generate_questions(model,m,combined_text, prompt, question_type, num_questions)
            else:
                st.write("No data available. Upload File again")
        
            st.success("Questions generated successfully!")
            st.markdown("### Generated Questions")

            st.write(questions)

            save_questions_to_db(questions,question_type)
 
    elif input_type == "Text Input" and text_input:
        combined_text = text_input
        save_data_to_db(combined_text)
        combined_text = get_data()
        if combined_text:
                    with st.spinner("Generating questions..."):
                        questions = generate_questions(model,m,combined_text, prompt, question_type, num_questions)
        else:
                st.write("No data available. Upload File again")
        
        st.success("Questions generated successfully!")
        st.markdown("### Generated Questions")

        st.write(questions)
            
        save_questions_to_db(questions,question_type)
    else:
        st.error("Please upload a PDF file or enter text, and enter a prompt.")
        combined_text = None



if st.sidebar.button("Show All Questions"):
    if buffer_collection.count_documents({}) == 0:
         st.write("No Questions Generated!")
    else:
        all_questions = get_all_questions()
        st.markdown("### All Stored Questions")
        i = 1
        for question in all_questions:

            st.write(f"*Question {i}*")
            st.write(question["Question"])
            try:
                if question["question_type"] == "MCQ":
                    st.write("*Options*")
                    st.write(question["Options"])
            except Exception as e:
                pass
            st.write("*Answer*")
            st.write(question["Answer"])
            i+=1

if st.sidebar.button("Send API Request") :
    store_in_api()


st.sidebar.markdown("<h2>PDF Splitter</h2>", unsafe_allow_html=True)
split_pdf_file = st.sidebar.file_uploader("Upload a PDF file for splitting", type=["pdf"])
page_ranges = st.sidebar.text_input("Enter page ranges (e.g., 10-30, 40-50)")
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
