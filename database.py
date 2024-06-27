import streamlit as st
from pymongo import MongoClient
import json
import http.client
import re

url = "rio24.azurewebsites.net"
access_token = "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZDQkMtSFM1MTIiLCJraWQiOiIwMDk2NzkwNjQ1QTQ1RkJGOEY5MzU4NjI1MEY0M0NFNUI2RkY0MDQ3IiwidHlwIjoiYXQrand0IiwiY3R5IjoiSldUIn0.Lxr-YIZB9jOmCKFksdhR1JBBhtN0qtfDTMFWRged9tCHg6nNXuopvzez5s8jnyudH57bnWNfrNuVHaX9xTCN5A4xOaGXZWY9vyfRC1OsPRCFYO3FHPwJiCZ43J8BVkftEehpyBzJt0CgF9HWpZXFZOitzw0uzYZzZKWcDOvtzgV6uI5Xhm877vgqSd-tK3tFPjaTPAbiVjcqDhZZo9HcnKiVJL8EE4YNs-8YvcF0agLquu1YXlvpvfN0fb4ZIjxbdAGVv2tem-sKuEyJiS591S6J06FoAg3MKro994fMohqEjf5PJ4-NWdiWz_24IrApz9gSobg_CNoMMtlfcKip1A.nVx9Q5mLt1d_vW_cB_W3xw.jf-_UlT8WNDC3EM5IwquM0A1eqj0q1SMrLfkl0MkAvp54nVRJvrf_X10MV-zRyF1bMnY0ducHnhVKCim9RTBMUbiz6NqhQi6YurWLdwWXCchu1s8qz0ICIBGrF2FQQjEV8F3ZayagxTVGHztIwWlxp-8kTYcVColPJlcaglOhn5fol0tKlEXSHDg6ceGbGxXNPjsQk_UenplbfTajwU6nAX3_yc6ujJ9nB9ZZ12lIdeE4CezTGNKmJJLHXfhROfPgSesWCIBhDtAH0bFnmzTOl9MPZMDZhueeWV4yFG0OAgeJbMgr6WyTWqfm1wMpvljDcmFBP3sCWOvgEA2K7HXTpFgLoV3FcTgue-3T876kD7vHJIC3wTa2wuZi6uBRNETRsbl-TZrc1G4TuQvhxr0D9okPGFg7O-DYyOLlGhGu3iq3xlieK1YKYwgsZQA_8AK9I4TaoVMPd-tNY3rrDtVaNbpXwjQOJX-tx5zmti4__vpxtPyNegt7eHoDUwWXIdN6dHWneOEhGuLfIqT_YIhJHQaP2Z4jgKb5IGcYNIu0ZG7w9WmBlkGhIcpk7bdaRcdW5DCPacvJDDz-BFIfD4z9xj8HTW7SsrPFom3LFWu6QUk7jcN1yTgaDknnfXLib_H6z-k0wcNqCOrlZvu5TfIi7LHl51miKpKZdo_09TC3a_fdkOkYfUHOfjqfHfAKpeefKBbqT5sLYMTAnpfWmQN1cSD-e96AEob1YXYu_pwOeabsSclyRSKXRJn2Sw9ziEe86fEoBYEEhCGRBcSiK_eIaDxnYQEGaEUD24yVX_RLPTePwAav63qRqib9g6F2X0x69cg4I1No9tuWsJfzR9OaSLXQbtAx5Om26PwHAxs2smB02Zk58shgUyWF9wop8J6l_gkASUZvx68bqpLaKUU2HpUt_1o2OSIZqkUBO-CsokWLtN-CM1QJJMvO3apdN4SE7SUUpwezl_ycW3QfREI_4-nhOgnr6dlnmG5Go3BSDcSrnWUir5UqQHiPDJaf7_7FmURn0eNHAGtuWV3d3TAIZHFNAb0Y6zdfBmhVfR4hlNlmiosx80rCeB6Q9NRcXAgSL-1TzBhIbVSmoUCHx26uu8yoZ7l_OsAgrl2f2Qo5GCtj-dpVdCA6FigeXeszGAE_MXKwW4yBGFqSy-BEXxS4KIQ1mhUTqF_PyudE3C9fKRz5HO3AscuIPop89Utb_1oOSyiRoUY18xT4aR71rSqTtvLEdG9rw8KxjTbuvwDzOTgdQeyItXBoLwmZ8kNE8AR2YiOmYOqKZzb4l9XWGgIhc90_SlEb2wybmiE8RYw4KX_m7tqxADOsCWmJFDE76Am4MPMemsvZLVQQU45M0xp-UPaVpjGwRhCOuraBBPy3XtTmL-27oW8jDiJdCPMTn-bcoESlpqH_-dz9vAgkBhGhW-iR0_zf0dqG1LVA_aNtkSubgw-goPU6LsAO2e2qbP8Fs4AxvQusFq7DI38eVp3Cg.4Q1_UrQ-AqvX5cFAl4EWn5B7IFtrq-Yo6jkMpE41ZO0"
mongo_connection_string = "mongodb+srv://goyalyash598:gym12345@cluster0.xxkdyhs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_connection_string)
db = client.questions_db
questions_collection = db.questions5
buffer_collection = db.buffer
data_collection = db.data

def send_insomnia_request(question):
    conn = http.client.HTTPSConnection(url) 
    if question["question_type"] == 'MCQ':
        temp = question.get("Options", [])
        payload = json.dumps({
            "Entity": {
                "QuestionText": question["Question"],
                "IsSubjective": False,
                "EQuestionType": 0,
                "BloomIndex": question["Bloom's Index"],
                "QuestionCommonDataId": "1",
                "EDifficultyLevel": 5,
                "IsActive": 1,
                "QuestionOptions": [
                    {
                        "QuestionOptionText": option.lower(),
                        "IsCorrect": "True" if option[option.find(":"):].lower() in question["Answer"].lower() else "False",
                        "SortOrder": "1",
                        "Notes": "12"
                    } for option in temp
                ]
            }
        })
    else:
        payload = json.dumps({
            "Entity": {
                "QuestionText": question["Question"],
                "IsSubjective": True,
                "EQuestionType": 0,
                "BloomIndex": question["Bloom's Index"],
                "QuestionCommonDataId": "1",
                "EDifficultyLevel": 5,
                "IsActive": 1,
                "QuestionOptions": []
            }
        })
    
    headers = {
        'cookie': "ARRAffinity=23564d5724d5738e1473c580c4ceefbbbe719a290964305a0fb76422b865e31c; ARRAffinitySameSite=23564d5724d5738e1473c580c4ceefbbbe719a290964305a0fb76422b865e31c",
        'Content-Type': "application/json",
        'User-Agent': "insomnia/9.2.0",
        'Authorization': f"Bearer {access_token}"
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
                options = [
                    f'a: {match[1].strip()}',
                    f'b: {match[2].strip()}',
                    f'c: {match[3].strip()}',
                    f'd: {match[4].strip()}'
                ]
                answer = match[5].strip()
                qa_pairs.append({
                        "Question": question,
                        "Options": options,
                        "Answer": answer
                    })

            jsonString = json.dumps(qa_pairs, indent=4)
    else:
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

    latexObj = json_to_latex(jsonObject, question_type)
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
            temp["Answer"] = f"\\textbf{{Answer}}: {answer_text}\n\n"
            temp["question_type"] = question_type
            temp["Bloom's Index"] = question["Bloom's Index"]
            latexObject.append(temp)
    elif question_type == "MCQ":
        for question in questions:
            temp = dict()
            question_text = question['Question']
            answer_text = question['Answer']
            temp["Question"] = f"\\textbf{{Question}}: {question_text}\n\n"
            temp["Options"] = question["Options"]
            temp["Answer"] = f"\\textbf{{Answer}}: {answer_text}\n\n"
            temp["question_type"] = question_type
            temp["Bloom's Index"] = question["Bloom's Index"]
            latexObject.append(temp)
    else:
        raise ValueError("Invalid question_type provided. It must be 'Descriptive', 'Fill in the Blanks', or 'MCQ'.")

    return latexObject

def store_in_api(question):
    try:
        response, status = send_insomnia_request(question)
        return response, status
    except Exception as e:
        return str(e), 500

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

def remove_question_from_buffer(question_id):
    buffer_collection.delete_one({"_id": question_id})
