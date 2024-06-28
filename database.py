import streamlit as st
from pymongo import MongoClient
import json
import http.client
import re

url = "rio24.azurewebsites.net"
access_token = "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZDQkMtSFM1MTIiLCJraWQiOiIwMDk2NzkwNjQ1QTQ1RkJGOEY5MzU4NjI1MEY0M0NFNUI2RkY0MDQ3IiwidHlwIjoiYXQrand0IiwiY3R5IjoiSldUIn0.WnGepHPAgs6oZFEle0p7wIgh0iOWOPrGIv4OBDtw-6DO5iCoR3iRx6Eczp-WvVLMfRDXVleK5GxTsTR8ZT91Fn0MyACw9flB9cYybFORZdLwfqIKdO9lNBMjR5EnEUkupgWKcFlp2IArqqen40cXdAeuz_st2VRYrYa4KvF5S-nPxTWOS_Vd_Iqy5REnta-J3hRS6VnOAU8MqNQGp6XoEE4p8aclsq50Tva4IuxJsl-446atHFrLNZOB8Y5CEjMBXHT2ur5Vpm7VRqOFtkH6ZCDhMWp1wVECp7U5iqd7_sUY5zf8i0hYdUf2uY_lBx5nd_SO-NCHkBoyhTfIKCDH8Q.8titnMLZrhTTlobZM4Hy6A.0zWEi_hoj9YLZjQipjsucXBdHohfa4Y2lvFLBQHnrWHEQtBs46Mtbba6IZuQ71fQGBnJPRcBvtMVle8_dvNgFq_wj_cRJsKRULh37KXAa4oGfRq4-3nbmoTcUzwbEtQfatwQpqdi9oYDwd15lG6cde-mEaE1cjkUFdp6i1pBUsw8q6DRekkbHdl3-EHyvRrbzOT_zHqnnidabX2izebCC6D75_PgSwgfOROyWEoAkgDtt8viRQfLHiq2WjCfut6ugpGR2ZoXnSE8bdsuxVnLR4Df3QgTosBqjQbMv50i1AcHrMvoznYri_ElpuTk9KFHiIbAm96ExoptorcGraAebcA6b-SeSXVbT15k6w0tMddrI4ZcBVvWqnZcvsIUSswL1vuRiKahuPMezPLYUUzTA-hZIqOXjza1fM1PSp6IiqEIJPnQf3VM-CHzz67AZDeHAWoAebWOZOMgGGcttFmMeAxCvpNg1-RNGvRGW7OxL_bEjVSUDbcuKEG6cMS9ZgK1lbiyvokIAtc3Ys1rpO37QWnHx6JWc4wTx5OZ0LVYMOf5GVS9pEkRC3RQtu4Mg1dg8cLYwo5JlAn8vcw9wyw_CYlxBP_dHAo61ZX-4f6f_fSRPRKmPYyK8-is2wIt4xiKKPKmkCS5CqFn7PjzKHr1SDYnJ9EzC2OhT05n4ITejvsGfqZo75jegxbSXI1ljyjwu3iyfvEDanimrVOAaI13tRLi1_Ulqw04kogzhprtJ5SCCRtE9MiElqV-RjiZ7rYcvKdmFet_tPq5LvTNhBFp5EPpCfrwCDrd0kjm5spqHCj3VqBI9eex3ehUcDOOvspuDkTqQ8NVZVFwSEDR6xLiuROAEghOo2zI-4xtDL6tEPbL1vNppb0ropMI89vKJco_NIkN89XArbGg_UYAroJ-1BvewTDOsHONjYbZd09sD_qrYR-F94UkOfdaD0gkMiXI55RXA2RJh6TSYeGLygSfvtwi0EZKOcGOYVq9vOE3D9fqDRYULuES0fyA926dxZqc4L5S1dnkJQ7zYrlajA1h0p7l6_st23Up-o9GcuINLSwaKEcdkeTPwMOkrVQBR-oQvoHo2V09F4T8MNZdhalQK_-FD9i36TowEtqe_3V5VZq6htaIZn4s06o8f36066NZVEXs2XHLkNjoYopeBWVI-TZnkz233to4i-ZFh3MYnVM0vFqwh6mu2a2DGCeYXVDtkLwpb4q8sXzxv7wZmbaVhtSP4G-ltZ7pBvRCvzdHg5uPU49JDR6BNbR0ylajo8LnBj6CXr4bYdnd36adyGwRsKtVR9GfLiyIG2DoIHLGQ9X2Wckr5Laay32x1NJK6t-dnzYZJ3RxFhtHQXnF7ZO87t9B7KVvxqJIF991DMtKPx9deKMM89pGDZLQYWow4L5mQouFUbe10Qb1mDajRFSW2ACdViOgZirSP3USYg7SAxSThAQPslPrnl77cAyyaOVRmOnVgXPNBWDXjpwzXA_fgg.GRZm0kwnyoAHgHsegKHXqVybzFFNep6PxbgCWynBr5Y"
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
