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
                "BloomIndex": question["Bloom's Index"],  # Adjust based on your needs
                "QuestionCommonDataId": "1",  # Adjust based on your needs
                "EDifficultyLevel": 5,  # Adjust based on your needs
                "IsActive": 1,
                "QuestionOptions": [
                    {
                    "QuestionOptionText": temp[0].lower() ,
                    "IsCorrect": "True" if temp[0][temp[0].find(":"):].lower() in question["Answer"].lower()  else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    },
                    {
                    "QuestionOptionText": temp[1].lower() ,
                    "IsCorrect": "True" if temp[1][temp[1].find(":"):].lower()  in question["Answer"].lower()  else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    },
                    {
                    "QuestionOptionText": temp[2].lower() ,
                    "IsCorrect": "True" if temp[2][temp[2].find(":"):].lower()  in question["Answer"].lower()  else "False",
                    "SortOrder": "1",
                    "Notes": "12"
                    },
                    {
                    "QuestionOptionText": temp[3].lower() ,
                    "IsCorrect": "True" if temp[3][temp[3].find(":"):].lower()  in question["Answer"].lower()  else "False",
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
                "BloomIndex": question["Bloom's Index"],  # Adjust based on your needs
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

def save_questions_to_db(questions, question_type, bloom):
    if(question_type=="MCQ"):
        pattern = re.compile(r'\*\*Question \d+:\*\* (.*?)\n\*\*Options:\*\*\n'
    r'a\) (.*?)\n'
    r'b\) (.*?)\n'
    r'c\) (.*?)\n'
    r'd\) (.*?)\n'
    r'\*\*Answer:\*\* (.*?)\n',re.DOTALL)
        matches = pattern.findall(questions)

        if not matches:
            pattern = re.compile(r'\*\*Question \d+:\*\* (.*?)\n\n\*\*Options:\*\*\n\n'
            r'a\) (.*?)\n'
            r'b\) (.*?)\n'
            r'c\) (.*?)\n'
            r'd\) (.*?)\n'
            r'\*\*Answer:\*\* (.*?)\n',re.DOTALL)
            matches = pattern.findall(questions)

        if not matches:
            st.write("JSON CONVERSION ERROR MCQ")
            return
        else:
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

            jsonString = json.dumps(qa_pairs, indent=4)
    elif(question_type=="Descriptive" or question_type=="Fill in the Blanks"):
        pattern = re.compile(r'\*\*Question \d+:\*\* (.*?)\n\*\*Answer:\*\*\s(.*?)(?:\n\n|\n$)', re.DOTALL)
        matches = pattern.findall(questions)
        if not matches:
            st.write("JSON CONVERSION ERROR Descriptive/Fill in the Blanks.")
            return

        qa_pairs = [{"Question": match[0].strip(), "Answer": match[1].strip()} for match in matches]
        jsonString = json.dumps(qa_pairs, indent=4)
 
    try:
        jsonObject = json.loads(jsonString)
    except json.JSONDecodeError as e:
        st.error(f"Failed to decode JSON: {e}")
        return

    bloom_index = {"Knowledge":0, "Comprehension":1, "Application":2,"Analysis":3,"Synthesis":4,"Evaluation":5}
    for i in jsonObject:
        i["question_type"] = question_type
        i["Bloom's Index"] = bloom_index[bloom]

    latexObj = json_to_latex(jsonObject,question_type)
    st.success("Successfully wrote in latex file")
    questions_collection.insert_many(latexObj)
    buffer_collection.insert_many(latexObj)
    st.success("Questions stored in MongoDB successfully")

def json_to_latex(questions, question_type):
    latexObject = []
    if question_type == "Descriptive" or question_type == "Fill in the Blanks":
        for question in questions:
            temp = dict()
            question_text = question['Question']
            answer_text = question['Answer']
            temp["Question"] = f"\\textbf{{Question}}: {question_text}\n\n"
            temp ["Answer"] = f"\\textbf{{Answer}}: {answer_text}\n\n"
            temp["question_type"] = question_type
            temp["Bloom's Index"] = question["Bloom's Index"]
            latexObject.append(temp)
    elif question_type == "MCQ":
        for question in questions:
            temp = dict()
            question_text = question['Question']
            answer_text = question['Answer']
            temp["Question"] = f"\\textbf{{Question}}: {question_text}\n\n"
            d1 = question["Options"]
            temp["Options"] = []
            for option in d1.keys() :
                temp["Options"].append(f"\\textbf{{Option}}: {option}) {d1[option]}\n\n")
            temp["Answer"] = f"\\textbf{{Answer}}: {answer_text}\n\n"
            temp["question_type"] = question_type
            temp["Bloom's Index"] = question["Bloom's Index"]
            latexObject.append(temp)
    else:
        raise ValueError("Invalid question_type provided. It must be 'Descriptive', 'Fill in the Blanks', or 'MCQ'.")

    return latexObject

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
    return document["text"] if document else None