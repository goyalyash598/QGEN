import streamlit as st
from pymongo import MongoClient
import json
import http.client
import re

url = "rio24.azurewebsites.net"
access_token = "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZDQkMtSFM1MTIiLCJraWQiOiIwMDk2NzkwNjQ1QTQ1RkJGOEY5MzU4NjI1MEY0M0NFNUI2RkY0MDQ3IiwidHlwIjoiYXQrand0IiwiY3R5IjoiSldUIn0.hpYpBIFTdKcUph-HfzRlD5ASFKTcqqOKCaWJec31xj85-6vjf_pUPLYyWX9k3Q6PPmRgHbnyYjwKYGUxOlIUrc3BhMDWSJ3K8MZEXUnwe0iM1L_2udCMq3IslPBnauvZtNNn73oJpXziv1rw66J3V1Bdy3Kd_XU1W6f_8s_SpHwB95JeulynEYp-TQFF7f-djscD5xJJIGChEwElZSmc59J8X5GltxvbBkQs1rkSUnp-6P4JKALbkp-fvYbEcP5g_uJ0Mw9yIz4RzOlfsGu2PDyHwojwVEJMy5HcFbNe3El_3EA2V9xLSGzG49h_-JAA-q3Rxf94HsNGP8NgJTu5Tg.ku6Bfx98GxeO_vlme2fz_w.TsbajnVmbXTQD9KzPKjSrlDm-YlJcRhjH0DmsANLfFgk-YqvHbXPy660zq7XsLl0F6My1JmreENvguxbKBlOolkxYAt5Znmky9GMZrq_Ip5KdoDeoHkEA9wjTuWFq96zkTt7G1_JLtdz68HDhm3sgTDvbULbhC8PhRoxZiA7NTZCvGu9pVuVl4exC3ahuCqHLZ2YXesZkHCJEBRLIuOLQNNSHCD4kqqBBpr4iAG022LlnfhbDRjShdAsFURFr0OxB8CaiUH8vtj_eoZJcWdEuGOBikzDWByqtwQ41QErQNQS5xSL4d2hG3oHYDr7fvANl8Nx6lV8dhRmP6pcDnOZkXTKnpK4tp3PRBB-9uuM2KCWm5rB6NBGAv9N9uOtuVv1g6S3i1j1rrgL_nZDjU68Ku8ZtCjOMKhkbvu6K2wnT-G6GAgSak-sVtB-CfCKQ72D1kwJZDoYE7n5r8n8XPZ0x3MBrgYHqOLWXcqGGgyxAHJ0A5_lEo3VyKlHm5BnH3GALfF-f4GL1bQiWqiulD-BybW5s6TE2TXMRlFfVmKDLZOz-OhZMNZqREB-jlkI5og40JhywKxxuJ9lfClY7i_BKYlb7ZMq2hd3I3VzYWTYtmll2m-NRkYlivygugD6M8hSfpox4HFhRya8NEwW_aONW4GVg7lATUrWjYVaQBTAVncl4_A9Nlym-Lk5l1qvUKK4vmvpnKu4Dprc6Idzbia4WBeOJMGSjoIVLtBZtAeRyRSGi5ceysn0CQ-MGZ47DZMPlTHtTExJgeZ2UthLK9pkcrfOa9tqAdjm1x8hAs8TJdCdITPeTtq850EY3BAfzNMG23o0NqMsiIcBjKjmMIYuExklKsbSY4E1wYEmjksmmmNNCZl9022cQwf6gN7G7_OklWQXCWKmjbxuK8aiAjqdJV26XSqh6X5PmHE5EuOHkotWmCvh4Ot2SAFLNI2l0ys0U8AiTttNzNmWKanRgl9dW528K2A6Iua5TAzDmtuZintDnRkw9rTBCyamV0Tcx0foKYi3drrOEcE4qhR5j4duRmoQ2b3LWSictdLx4KktiS1Kh0yInMmgzsm-faIJsT7KYQ_qfNlWGdWIKKxf9MpAV178H87gGSpyPKvBWRDZuNoPmkegPjkn7jbEbYswREuR9-HFP53Q7CwEK30nVADW-ZHFckQpxIiP-aXnm3jZfhP_a-yCQRCOZKmk08XkZGxysnbxGrKgL82fLqWMBXU4yd7LcMSvO_wuNZcmiztqkW6rQZeMt7z73ar9H8Y_V-HdkBSITNpvEHUA7OO7IrUu_AcO3hWjmuloHeV8kdzTc8YZ7mhej-Vjx4wd2zWcuLQ3HO9RqMLX178W8M_z0i2oB5y5gJvskx7tShJe-0cldfU_AM-wgIyWgto2ofCDQInkE6DsCEI-pGCEvPiUNig2oJZHVMw9uLEfIHUBN3BYqFZyWIabsPV_6P9V3HRatOwFu_AFCjsrEzHIFCHuo84UEQ.cbD3nUCGUOilsnG3ZJFKfaoDqWIlN17IIzEfU7LXdQI"

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
