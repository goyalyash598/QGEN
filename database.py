import streamlit as st
from pymongo import MongoClient
import google.generativeai as genai
import json
import requests

api_key = st.secrets["api_keys"]["genai_api_key"]
genai.configure(api_key=api_key)

#CAUTION!!!!!  Here the  Model Should only be  gemini-1.5-pro
model = genai.GenerativeModel("gemini-1.5-pro" ,
                              generation_config={
                                "temperature":0.3,
                                "max_output_tokens" : 4096
                              },
                              safety_settings=[
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
])
mongo_connection_string = st.secrets["mongo"]["connection_string"]
# st.write(f"MongoDB Connection String: {mongo_connection_string}")

client = MongoClient(mongo_connection_string)
db = client.questions_db
questions_collection = db.questions

data_collection = db.data



def save_questions_to_db(questions,question_type):
    # prompt = f"""The following is the questions generated in the {question_type} format i want you to convert
    # convert this into purely JSON format (There should be nothing in output except the JSON output)
    #  so that i can store it properly: {questions}"""
    prompt = f"""I want you to Change the Generated Questions in a dictionary format. Each Dictionary should have a key called questions that will store the question and a key called answer that will store the answer.
                If the question is a MCQ I want you to make a key called Options that will store the Options in a list. Do Not return anything else only the Questions.Each Key should be enclosed in double quotes as JSON format Requires.
                Here is the list of Questions {questions}"""
    res = model.generate_content(prompt)
    jsonString = res.text
    index1 = jsonString.find("{")
    index2 = jsonString.rfind("}")
    jsonString= f"[{jsonString[index1:index2+1]}]"
    jsonString = jsonString.replace("'", '')
    # print(index1)
    # print(index2)
    # jsonString = jsonString[8:len(jsonString)-4]
    # print(jsonString)
    # print(type(jsonString))
    # print(jsonString[index1:index2+1])
    try:
        jsonObject = json.loads(jsonString)
    except json.JSONDecodeError as e:
        # print(jsonString)
        # print(type(jsonString))
        st.error(f"Failed to decode JSON: {e}")
        return
    # print(jsonObject)
    # print(type(jsonObject))
    questions_collection.insert_many(jsonObject)
    st.success("Questions stored in MongoDB successfully")
    
    try:
        x = sendRequest(jsonString)
        st.success("Request sent!")
        st.write(x.status_code)
    except Exception as e:
        print(f"Error in sending request:{e}")
    


def get_all_questions():
    return list(questions_collection.find())

def save_data_to_db(data):
    filter = {"text": {"$exists": True}}
    data_collection.replace_one(filter, {"text":data}, upsert=True)

def get_data():
    filter = {"text": {"$exists": True}}

    # Find the document
    document = data_collection.find_one(filter)
    return document

def sendRequest(jsonObject) :
    #Extracting URL and Token from Secrets.toml
    url = st.secrets['post']['url']
    # myobj = {'somekey': st.secrets['post']['key']}
    headers = {
        'Authorization': st.secrets['post']['access_token']
    }
    # IF any Error occurs in this We can provide the same here, the code is commented for now
    #########################################
    # url = "Put The URL here"
    # # myobj = {'somekey': st.secrets['post']['key']}
    # headers = {
    #     'Authorization': "Put the Token Here"
    # }
    ############################################

    # Questions = get_all_questions()
    # for question in jsonObject:
    #     print(question)
    #     x = requests.post(url, json=json.dumps(question), headers=headers)
    x = requests.post(url, json=jsonObject, headers=headers)
    return x
    # st.write(x.status_code)
    # print(type(x.content))
    

