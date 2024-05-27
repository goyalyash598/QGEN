import streamlit as st
from pymongo import MongoClient

mongo_connection_string = st.secrets["mongo"]["connection_string"]
st.write(f"MongoDB Connection String: {mongo_connection_string}")

client = MongoClient(mongo_connection_string)
db = client.questions_db
questions_collection = db.questions

def save_questions_to_db(questions):
    questions_to_insert = [{"text": question} for question in questions]
    questions_collection.insert_many(questions_to_insert)
def get_all_questions():
    return list(questions_collection.find())