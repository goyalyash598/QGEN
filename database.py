import streamlit as st
from pymongo import MongoClient
import json
import http.client
import re

url = "rio24.azurewebsites.net"
access_token = "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZDQkMtSFM1MTIiLCJraWQiOiIwMDk2NzkwNjQ1QTQ1RkJGOEY5MzU4NjI1MEY0M0NFNUI2RkY0MDQ3IiwidHlwIjoiYXQrand0IiwiY3R5IjoiSldUIn0.UiAwIST_MF9z-2wexK7pqqE780OvuGc_sVqB_XA1yDmIMFbhag9bnJ5Kr3wsT9gYaCH1tao4ES8PjSyUFFAwM06QDxa9PLh7E0a9gdX7toa26hHcpnIl6uzuIxxow-WC5Q1zgFv3GZJUrlpvsV-ru3A4mibWPrwXgwPV47nx_VugcmG6D65RkqMnvOeWx1yNYGq5prmajA_RlOJwTWfQd7dbR2cePxD8H1svEQKzH31oaLI8i0RwQ98mVwMi0xPmArAGJfiIWRFufnBCjuajwIpQeFSqHHpDT2S8daENb9qq9RZwbm8bwUE3TZFjUt8iYYxjxQhxR4Oz_KuwzqvGSg.fekmwNjXpx2zgy7f8tUHLg.TSBS3sBjHX0-NnrxdIfrRV8OXiM97ES0xPhPiCgTm0zSymFK4HWJZIWNVC8gsf63uaaEk7vB5sJeD3ux4p7h5DuaqD1VJeR0Eppuv-zeoO9vti-e-eilts3Vx7YPolCIAzb1S9gwrz2woSdim1yp8t6nVVxdaf1HkwHQJFyGJpEQp1PnojivvuoiTXv7_rvqaRsrue49OSxSYNTuTerITEkhkxo3-rowZPw3kCqCfMwng6ZSkXq9bdO2HzAlOylCUbBMPLYl7xouQ3UQ7cZiyvyiOuAzCj-EnVO_pFNr_VQ1yUjeCftPCg41gtoqXq91af38954NWuPBU9eWm1N37Y7X92CzWOzIt388gZ0wZH6V4CA2d76eHMr2j2346W__IdUAVU0vnKVik_3ULrvk44Io7c-xqF7rBTPO7qRSdnvgpSz1TjIYpcnEYMgSWRgpP3FPnzQZOvmTAKTE3Wk2c5LoSkdX38ocq7tfuTt80oUUdBOMuG7EBurrtKbkf1SK-kjEDvH25kxKH48cv8A6Ycw53kQgoj5StKo9-JHod0RH4B193FZNIKWPWz-C9I5BXwVVLClPMYJKbQlKVK9CzqiqzYFfD8_yaqBzbQe9MdhvvH42f1fiNZtyzA7FEpmUnPF_EWGNsiEFh8-BaFnWSCY31W3Eo2voY1dOLd-N67Lr3Uz0g8KqZjXxUNdzeMKq7AvfSNjzVLOtNybZThDms-r-WJCDyC8ysoB40JvWWyGEgr7eonqrzVk3IXWPRwEgXXthojUuCyH_UYOd3622IyANmp7sYod_VaGyzmfv_0kNBDcGAB6MHowcLA0oTT3a5XbRIG6MzxxqFmB8LEnz0Ml98Ty32VkeYynpfgJXbWNMoEpXbzKAiFNblLJcjVCMsNQFL6HRtZCTQayaD1CsDeqwVuy4c7mOwqY_HZ45K8RkGrKaHUGwbIoSOA-ILcoyUovj5jADMxfVDeeIZK-SJ2Ck-_5QFcia2gKiGx_ST2jCfvBMnyqbb2Mmolt2UR0eE-jE0CS_uX53-cWFMlREb5iqs2MnXiI7lftLT5gAzIK8duppsJ6mMU7pcW51jTTxqxknnAt8L_pOqCZFg92TtnBXXBEHuXg1XKHvseQPZbCKra0BUaikDhSZgukyWfQKrh3RaQyqMv-mHgqtFaqnEFc_H2c0wL_peq1rPl3TLMa9r14uJPGfnrorG58pmfYPqk5AVvOnPn2-kV4awF0b9cOo9z2pyyR9aJ4B3V_V5YWD8hjKJgRHyarBqs6avXOddJNxWDKDVfYTplmLmtOPrqldXi6pLuF9P74fYeQS_b2Gl2Oirn7BifNNy6oqsiOQ7bMJd4Xql52Varn9aBjrshgQxgd08H_DhAZyhhDeN9HvgL1kLez1riuJxosbK5PNarOEm9yPSwbHyrskfq5M5EgnnJdPVD1OvXpPyHwHKJtQPlXzooO6GBZUNPpcyqgFSIta6Lcqvm1M88VdY-zzew.rxS7q5qmVCmiO4IUsvBP97LJqRDEHQTjUYzqjtTZ2bY"  # Bearer token field left empty as requested

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
