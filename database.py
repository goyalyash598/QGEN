import streamlit as st
from pymongo import MongoClient
import google.generativeai as genai
import json
import http.client

# Configure API key for generative AI
api_key = st.secrets["api_keys"]["genai_api_key"]
genai.configure(api_key=api_key)

# Set up generative model
model = genai.GenerativeModel("gemini-1.5-pro", generation_config={
    "temperature": 0.3,
    "max_output_tokens": 4096
}, safety_settings=[
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
])

# MongoDB connection
mongo_connection_string = st.secrets["mongo"]["connection_string"]
client = MongoClient(mongo_connection_string)
db = client.questions_db
questions_collection = db.questions1
data_collection = db.data

def send_insomnia_request(question,question_type):
    conn = http.client.HTTPSConnection(st.secrets["post"]["url"]) 
    if question_type == 'MCQ':
        temp = question.get("options", []) 
        payload = json.dumps({
            "Entity": {
                "QuestionText": question["question"],
                "IsSubjective": False,  # Set this based on your actual question type
                "EQuestionType": 0,  # Adjust based on your needs
                "BloomIndex": 0,  # Adjust based on your needs
                "QuestionCommonDataId": "1",  # Adjust based on your needs
                "EDifficultyLevel": 5,  # Adjust based on your needs
                "IsActive": 1,
                # "QuestionOptions": 
                "QuestionOptions": [
                    {
                    "QuestionOptionText": temp[0],
                    "IsCorrect": "True" if question["answer"] == temp[0] else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    },
                    {
                    "QuestionOptionText": temp[1],
                    "IsCorrect": "True" if question["answer"] == temp[1] else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    },
                    {
                    "QuestionOptionText": temp[2],
                    "IsCorrect": "True" if question["answer"] == temp[2] else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    },
                    {
                    "QuestionOptionText": temp[3],
                    "IsCorrect": "True" if question["answer"] == temp[3] else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    }
                    ]
 
            }
        })
    else:
        # temp = question.get("options", []) 
        payload = json.dumps({
            "Entity": {
                "QuestionText": question["question"],
                "IsSubjective": True,  # Set this based on your actual question type
                "EQuestionType": 0,  # Adjust based on your needs
                "BloomIndex": 0,  # Adjust based on your needs
                "QuestionCommonDataId": "1",  # Adjust based on your needs
                "EDifficultyLevel": 5,  # Adjust based on your needs
                "IsActive": 1,
                "QuestionOptions": []
            }
        })
    
    print(payload)


    headers = {
        'cookie': "ARRAffinity=23564d5724d5738e1473c580c4ceefbbbe719a290964305a0fb76422b865e31c; ARRAffinitySameSite=23564d5724d5738e1473c580c4ceefbbbe719a290964305a0fb76422b865e31c",
        'Content-Type': "application/json",
        'User-Agent': "insomnia/9.2.0",
        'Authorization': f"Bearer {st.secrets['post']['access_token']}"
    }

    conn.request("POST", "/Services/ExamSpace/Question/CreateQuestionWithOption", payload, headers)
    res = conn.getresponse()
    data = res.read()

    # Debugging logs
    print("Request Payload:", payload)
    print("Response Status:", res.status)
    print("Response Data:", data.decode("utf-8"))

    return data.decode("utf-8")

def save_questions_to_db(questions, question_type):
    prompt = f"""I want you to Change the Generated Questions in a dictionary format. Each Dictionary should have a key called question that will store the question and a key called answer that will store the answer.
                If the question is a MCQ I want you to make a key called Options that will store the Options in a list. Do Not return anything else only the Questions. Each Key should be enclosed in double quotes as JSON format Requires.
                Here is the list of Questions {questions}"""
    res = model.generate_content(prompt)
    jsonString = res.text
    index1 = jsonString.find("{")
    index2 = jsonString.rfind("}")
    jsonString = f"[{jsonString[index1:index2 + 1]}]"
    jsonString = jsonString.replace("'", '')

    # Debugging logs
    print("Generated JSON String:", jsonString)

    try:
        jsonObject = json.loads(jsonString)
    except json.JSONDecodeError as e:
        st.error(f"Failed to decode JSON: {e}")
        print(f"JSON Decode Error: {e}")
        return

    # Debugging logs
    print("JSON Object:", jsonObject)

    questions_collection.insert_many(jsonObject)
    st.success("Questions stored in MongoDB successfully")

    try:
        for question in jsonObject:
            # print(question)
            response = send_insomnia_request(question,question_type)
            st.write(response)
            print("Response from Insomnia Request:", response)
        st.success("Requests sent!")
    except Exception as e:
        st.error(f"Error in sending request: {e}")
        print(f"Error in sending request: {e}")

def get_all_questions():
    return list(questions_collection.find())

def save_data_to_db(data):
    filter = {"text": {"$exists": True}}
    data_collection.replace_one(filter, {"text": data}, upsert=True)

def get_data():
    filter = {"text": {"$exists": True}}
    document = data_collection.find_one(filter)
    return document
