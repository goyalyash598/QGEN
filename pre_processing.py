import os
import base64
import io
import fitz 
from PIL import Image
import streamlit as st
import google.generativeai as genai
import anthropic
from database import *
from openai import OpenAI
import requests

genai_api_key = "AIzaSyAtWNEpZbaNOQVcuKlk-xzWJz3sAT7sh08"
api_key_ant = ""
openai_api_key = ""


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
            smask = img[1]
            if(smask == 0):
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                images.append((page_num, img_index, image_data))
           
        extracted_text += text.strip()

    # os.makedirs("Images", exist_ok=True)

    image_merge = []
    #Convert Image to IOBytes for for later Converting to Base64
    for page_num, img_index, image_bytes in images:
        try:
            image_stream = io.BytesIO(image_bytes)
            image = Image.open(image_stream)
            image_merge.append(image)
            # image.save(os.path.join("Images", f"image_{page_num}_{img_index}.png"))

        except Exception as e:
            with open("Error logs(bytes).txt","w") as f:
                f.write(str(e))
    # print(len(image_merge))
    return extracted_text,image_merge

def preprocess_images(image_merge,model,m):
    genai.configure(api_key=genai_api_key)
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
    modelImage = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest", 
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
    image_descriptions = []
    
    # step size determines the stacking of images
    step = 5
    for i in range(0,len(image_merge),step):
        # print(i)
        combined_image = combine_images(image_merge[i:i+step])
        image_path = "temp_image.jpg"
        try:
            buffer = io.BytesIO()
            combined_image.save(buffer, format="JPEG")  # Preserve original format
        except Exception as e:
            with open("Error logs(Buffer).txt","w") as f:
                f.write(str(e))
        
        try:

            image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            buffer.close()

            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_base64))
                image_file = upload_to_gemini(image_path)

            
                    
            chat_session = modelImage.start_chat(
                    history=[
                            {"role": "user", "parts": ["Understand the image and learn the concepts in it, summarize the given image", image_file]},
                            {"role": "model", "parts": ["Your description of the image goes here."]},
                        ]
                    )
            response = chat_session.send_message("Understand the image and Describe the image in more detail.").text
         
            image_descriptions.append(response)

            # print(image_descriptions)

            os.remove(image_path)
        except Exception as e:
                st.write(f"Error processing image: {e}")
                

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
        # Assuming a grid layout with a fixed number of columns
        cols = 2
        rows = (len(images) + 1) // cols
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        combined_image = Image.new('RGB', (cols * max_width, rows * max_height))

        for idx, img in enumerate(images):
            x_offset = (idx % cols) * max_width
            y_offset = (idx // cols) * max_height
            combined_image.paste(img, (x_offset, y_offset))

    # print(type(combined_image))
    return combined_image

def handle_pdf_file(pdf_file,model,m):
    pdf_path = f"temp_{pdf_file.name}"
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getbuffer())
    text, images = extract_text_and_images(pdf_path)
    num_images = len(images)
    # st.write(f"Number of images extracted: {num_images}")
    if(num_images < 30):
        # st.write(f"Number of images extracted: {num_images}")
        image_descriptions = preprocess_images(images,model,m)
        combined_text = text + " ".join(image_descriptions)
    else:
        combined_text = text
    os.remove(pdf_path)
    return combined_text     

def gpt_description(image_base64):

    # get the OpenAI API Key
    api_key = openai_api_key

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }

    payload = {
    "model": "gpt-4o",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "What’s in this image?"
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image_base64}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # print(response.json()["choices"][0]["message"]["content"])

    return response.json()["choices"][0]["message"]["content"]

def model_selection(m):
    if m == "Gemini":
        genai.configure(api_key=genai_api_key)
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
        return model
    elif m == "Claude":
        api_key_cld = api_key_ant
        client_claude = anthropic.Anthropic(api_key=api_key_cld)
        return client_claude
    elif m == "OpenAI ChatGPT": 
        model = OpenAI(
        # This is the default and can be omitted
        api_key=openai_api_key,
            )
        return model
    
def generate_questions(model,m, combined_text, prompt, question_type,question_level, bloom,language, num_questions=10):
    if question_type == "Descriptive":
        user_prompt = fr"{prompt}\n\nBased on the following text, generate {num_questions} detailed descriptive questions of {question_level} Difficulty Level with correct answer only, Also ensure the the questions are {bloom} based as per Bloom's Taxonomy:\n\n{combined_text}.The questions should be in this {language}.\n The format of the output should match the following Regex- \*\*Question \d+:\*\* (.*?)\n\*\*Answer:\*\*\s(.*?)(?:\n\n|\n$) \n For mathematical equations only keep them in format example $$f(x) = x^2 + 2x + 1$$"
    elif question_type == "MCQ":
        user_prompt = fr"""{prompt}\n\nBased on the following text, generate {num_questions} Multiple Choice Question(MCQs) and four options each and Answer of {question_level} Difficulty Level, Also ensure the the questions are {bloom} based as per Bloom's Taxonomy:\n\n{combined_text}.The questions should be in this {language}.\n The format of the output should match the following Regex- \*\*Question \d+:\*\* (.*?)\n\*\*Options:\*\*\n'
                        r'a\) (.*?)\n'
                        r'b\) (.*?)\n'
                        r'c\) (.*?)\n'
                        r'd\) (.*?)\n'
                        r'\*\*Answer:\*\* (.*?)\n For mathematical equations only keep them in format example $$f(x) = x^2 + 2x + 1$$"""
    elif question_type == "Fill in the Blanks":
        user_prompt = fr"{prompt}\n\nBased on the following text,Strictly generate {num_questions} fill in the blank questions only with correct answer. DO not Generate Descriptive or One word Question.The Question Should have a missing word replaced by blank that is the answer and the Difficulty should {question_level},  Also ensure the the questions are {bloom} based as per Bloom's Taxonomy:\n\n{combined_text}.The questions should be in this {language}.\n\n The format of the output should match the following Regex- \*\*Question \d+:\*\* (.*?)\n\*\*Answer:\*\*\s(.*?)(?:\n\n|\n$) \n For mathematical equations only keep them in format example $$f(x) = x^2 + 2x + 1$$"
    # print(user_prompt)
    # try:
    if(1):

        if m == "Gemini":
            chat_session = model.start_chat(history=[{"role": "user", "parts": [user_prompt]}])
            # response = chat_session.send_message(f"Please provide {num_questions} questions as requested, without any additional context.")
            response = chat_session.send_message(f"Please do as Asked above.")
            # print(type(response.text))
            return response.text

        elif m == "Claude":
            response = model.messages.create(
            model = 'claude-3-opus-20240229',
            max_tokens = 1024,
            messages = [{"role":"user","content": user_prompt + "\n\nPlease provide questions as requested, without any additional context."}]
            )

           

            return response.content[0].text
        
        else :

            response = model.chat.completions.create(
                model="gpt-4o",
                messages=[

                    {"role": "user", "content": user_prompt + "\n\nPlease provide questions as requested, without any additional context."}
                ],

            )
            return response.choices[0].message.content

    # except Exception as e:
    #     st.error(f"Error generating questions: {e}")
    #     return []

