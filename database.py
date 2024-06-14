import streamlit as st
from pymongo import MongoClient
import json
import http.client
import re

mongo_connection_string = st.secrets["mongo"]["connection_string"]
client = MongoClient(mongo_connection_string)
db = client.questions_db
questions_collection = db.questions5
buffer_collection = db.buffer
data_collection = db.data

def send_insomnia_request(question):
    conn = http.client.HTTPSConnection(st.secrets["post"]["url"]) 
    if question["question_type"] == 'MCQ':
        temp = question.get("Options", [])
        payload = json.dumps({
            "Entity": {
                "QuestionText": question["Question"],
                "IsSubjective": False,  # Set this based on your actual question type
                "EQuestionType": 0,  # Adjust based on your needs
                "BloomIndex": 0,  # Adjust based on your needs
                "QuestionCommonDataId": "1",  # Adjust based on your needs
                "EDifficultyLevel": 5,  # Adjust based on your needs
                "IsActive": 1,
                # "QuestionOptions": 
                "QuestionOptions": [
                    {
                    "QuestionOptionText": temp['a'].lower() ,
                    "IsCorrect": "True" if temp['a'].lower() in question["Answer"].lower()  else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    },
                    {
                    "QuestionOptionText": temp['b'].lower() ,
                    "IsCorrect": "True" if temp['b'].lower()  in question["Answer"].lower()  else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    },
                    {
                    "QuestionOptionText": temp['c'].lower() ,
                    "IsCorrect": "True" if temp['c'].lower()  in question["Answer"].lower()  else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    },
                    {
                    "QuestionOptionText": temp['d'].lower() ,
                    "IsCorrect": "True" if temp['d'].lower()  in question["Answer"].lower()  else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    }
                    ]
 
            }
        })
    else:

        payload = json.dumps({
            "Entity": {
                "QuestionText": question["Question"],
                "IsSubjective": True,  # Set this based on your actual question type
                "EQuestionType": 0,  # Adjust based on your needs
                "BloomIndex": 0,  # Adjust based on your needs
                "QuestionCommonDataId": "1",  # Adjust based on your needs
                "EDifficultyLevel": 5,  # Adjust based on your needs
                "IsActive": 1,
                "QuestionOptions": []
            }
        })
    
    headers = {
        'cookie': "ARRAffinity=23564d5724d5738e1473c580c4ceefbbbe719a290964305a0fb76422b865e31c; ARRAffinitySameSite=23564d5724d5738e1473c580c4ceefbbbe719a290964305a0fb76422b865e31c",
        'Content-Type': "application/json",
        'User-Agent': "insomnia/9.2.0",
        'Authorization': f"Bearer {st.secrets['post']['access_token']}"
    }

    conn.request("POST", "/Services/ExamSpace/Question/CreateQuestionWithOption", payload, headers)
    res = conn.getresponse()
    data = res.read()

    return data.decode("utf-8"), res.status

def save_questions_to_db(questions, question_type):
    
    if(question_type=="MCQ"):
        pattern = re.compile(r'\*\*Question \d+:\*\* (.*?)\n\*\*Options:\*\*\n'
    r'a\) (.*?)\n'
    r'b\) (.*?)\n'
    r'c\) (.*?)\n'
    r'd\) (.*?)\n'
    r'\*\*Answer:\*\* (.*?)\n',re.DOTALL)
        matches = pattern.findall(questions)

        # Check if matches is empty
        if not matches:
            st.write("JSON CONVERSION ERROR MCQ")
            return
        else:
            # Construct a list of dictionaries with keys "Question", "Options", and "Answer"
            qa_pairs = []
            for match in matches:
                question = match[0].strip()
                options = {
                    'a': match[1].strip(),
                    'b': match[2].strip(),
                    'c': match[3].strip(),
                    'd': match[4].strip()
                    }
                answer = match[5].strip()
                qa_pairs.append({
                        "Question": question,
                        "Options": options,
                        "Answer": answer
                    })


            # Convert the list to a JSON string
            jsonString = json.dumps(qa_pairs, indent=4)
    elif(question_type=="Descriptive"):
        pattern = re.compile(r'\*\*Question \d+:\*\* (.*?)\n\*\*Answer:\*\*\s(.*?)(?:\n\n|\n$)', re.DOTALL)
        # Find all matches in the text
        matches = pattern.findall(questions)
        # Check if matches is empty
        if not matches:
            st.write("JSON CONVERSION ERROR Descriptive/Fill in the Blanks.")
            return

        # Construct a list of dictionaries with keys "Question" and "Answer"
        qa_pairs = [{"Question": match[0].strip(), "Answer": match[1].strip()} for match in matches]

        # Convert the list to a JSON string
        jsonString = json.dumps(qa_pairs, indent=4)
    else: 
        pattern = re.compile(r'\*\*Question \d+:\*\* (.*?)\n\*\*Answer:\*\*\s(.*?)(?:\n\n|\n$)', re.DOTALL)

        # Find all matches in the text
        matches = pattern.findall(questions)
        # Check if matches is empty
        if not matches:
            st.write("JSON CONVERSION ERROR Descriptive/Fill in the Blanks.")
            return

        # Construct a list of dictionaries with keys "Question" and "Answer"
        qa_pairs = [{"Question": match[0].strip(), "Answer": match[1].strip()} for match in matches]

        # Convert the list to a JSON string
        jsonString = json.dumps(qa_pairs, indent=4)
 
 
    try:
        jsonObject = json.loads(jsonString)
    except json.JSONDecodeError as e:
        st.error(f"Failed to decode JSON: {e}")

        return

    # Debugging logs
    for i in jsonObject :

        i["question_type"] = question_type
    questions_collection.insert_many(jsonObject)
    buffer_collection.insert_many(jsonObject)
    st.success("Questions stored in MongoDB successfully")


def store_in_api():
    jsonObject = get_all_questions()
    try:
        for question in jsonObject:
            response, status = send_insomnia_request(question)
            st.write(response)

        st.success(f"Requests sent! Status code {status}")
    except Exception as e:
        st.error(f"Error in sending request: {e}")
 
def get_all_questions():
    return list(buffer_collection.find())

def clear_data():
    buffer_collection.delete_many({})

def save_data_to_db(data):
    filter = {"text": {"$exists": True}}
    data_collection.replace_one(filter, {"text": data}, upsert=True)

def get_data():
    filter = {"text": {"$exists": True}}
    document = data_collection.find_one(filter)
    return document