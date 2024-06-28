import streamlit as st
from pymongo import MongoClient
import json
import http.client
import re

url = "rio24.azurewebsites.net"
access_token = "eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZDQkMtSFM1MTIiLCJraWQiOiIwMDk2NzkwNjQ1QTQ1RkJGOEY5MzU4NjI1MEY0M0NFNUI2RkY0MDQ3IiwidHlwIjoiYXQrand0IiwiY3R5IjoiSldUIn0.ICNtG8D6CuWBaq8bM17QSEGBFGJaO5ToM39i5ie_ljslX72goqi4dggEGhmH-xEZPWTY0LL1YnTuWkeHBLTqvzMdBMs7_5PGXMBj_jp0XUQSQwQ7JZYE2GFnux-k-u0v4cy-CiELPwwplJGn1_WYwCc_-Fh4_fXTPo3HNeAk-AnQBpxAC0wJkZ0eMkefYQcsUkANm7DCqZTfw31FsgfdgUuhdhpJEYfSQAChebCvGRzZ38kVmpt62-SBDy8irt_OJ4-_yQY9O5uSFeKFL_b3Q77sqFa7wx47BNIP3XyM9nvXYzzS2-HDDFnj3738mpsdZuRPVZy7LV88RGWC-ZNKDQ.mj0uBzmGa2oLp6XHmQLGsw.lzdTRi8gdi64o9t-xPg8f7vgIpC8bdMAlA0uhfLYfUK9Np5SkJCS4-xxEySlEZ3R-cfTqqolNv2yCsFeeBx8PRz2EZfibP1pRt3FA26BQxrU3A9nIgdXGlH-am5hqZMGjPRhoNPskYPOZmBJ2YBQg5LtY-L6EPMUL8eS4YuW9Qj8mlY4jXUUvxbVlexoEup632_WifmCRh3SMSH9E_Sz7YNhzVSD0cTol7Wz1DvdHwlf4dsMcibLvnhVZYPreee-sPDFWDD_61tSuq-BxX6PRH-a6CSPBPdqp7J2uZ9DLOK1YgQOD0VAHiJXv9ec2oM4jJHkvLvzj2LcDWwG-x8JXOEfIOi4j5YBPDhmh_XFRvZTt8zIOIxF0-hVwFrbuDbRycIZLcsfrctQWHzy2VjvOIfc8-SQiB9GaaeBIUpYEmLoS6Z9eQyc897Esn2JgCxenEKetxXpdPnkXntN4FOP0jCF0_F09tTQLrG8F4zJCqBFUsPAE2kEQavECuaVlRYezmvSYl2jz-THhMjtitCb3FZ9r0ax13gwNWeaBjp33i7HkE8p6GAPkUSwfdqLwjdgrX8QMGaKzd9si6_NDXEtRGSkqR7u1J4M_ut99rbbwKjwu-c6dJMAjyhARt2fLe5cAnSDRPFDeOwGvMoqE978rtxgnc_LfXjDIhZGpbntCC_cBY40isHDGRd1s3hYg8PZDTNZVIE8uYhE6MgpG02wlT3rYEdB5Wmfy9rfcqQouUqIx3y15Vo5J0JZrzJe6XFydPaFRBg6ZcXGU81aGr_SgLrwm1XxeGwQWriZ94DxV_nB_4qez8rQzEUPZ7oShMoYZbXzHh1fUU9O20FdT8y909IY_og89lnuZpkMJSpnYmIca3qCGbRmJ5qo9HUns00vBs0FxOv24aqI0Tg_G1lz6Bg5eAl9GLy9jJvwHCx_PuYOnqvoDw4CsupUJuAUoAsIlKFgQNr3JlJeUhk2wU4DurAfEUovAsAv6RsFtv7JYLEe7qumaRET3GwfyqFjkmGyON96SH7djx4ugbM1fhzgIExxsPLWSNE2qrsCszOxtVI-eCW1TVot5yw5hR2ft684e-TShpqdaxDCQ4CCJqLIbkWrUItUWMFd6ooz3CadYOHyTZkIVj0PLnFCRP0Xtv1IQOKbnHsFJog2RiPFS2Po8R2E6w7YiYQrrrD9BBw4pFWVxIEE_reiqTLtaP1pq3qsjb60LQgMZCKEu4rSh52ncLNvSyVrQtMqQOZtBjjHY12DXVXa6_IpTcGTWQptgz2fXs7TmwA1a0AUZ1b9-RevOYY-5dwOUbMxJwtaUl_QJIG24irdvWdDrlq6yJBZKK4BSHsaPDQySvGUMEF0-J8SrRAzf_GkRCaMKS90L_CqQzTvIt-5rhMn9cgE6v_HOuNCRLwVh5MgOoQfTgyqjVxOGx5X7HxpeQtkv_xAD38YMFm7CmOqou58moCPDEOusvz62dpGwqwEavmU7xPnhfVoUA.5u3AJRoSMH48k2UlFjEy6MORwc2GXrG1XNMtUIg9HXY"

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
