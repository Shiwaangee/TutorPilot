import streamlit as st
import requests
import os
from dotenv import load_dotenv

# we run this to inject env variables into the python environment. Later we need our os to extract the variable from
# the python environment.
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

st.title("TutorPilot – Powered by OpenRouter")

# subject = st.selectbox("Choose subject:", ["DSA", "Project Management", "Entrepreneurship", "Custom"])
subject = st.selectbox(
    "Choose subject:",
    ["DSA", "Project Management", "Entrepreneurship", "Custom"],
    index=1,
    help="Select the subject you want help with."
)
if subject == "Custom":
    custom_subject = st.text_input("Enter your custom subject:")
    if custom_subject:
        subject = custom_subject  # Replace "Custom" with actual input

mode = st.radio("Choose mode:", ["Exam Mode", "Concept Mode", "Quiz Mode"])
user_input = st.text_input("Ask your question:")

if user_input:
    system_prompt = f"You are a helpful tutor for {subject}. Use {mode} style. Explain simply and clearly."
    
        #     system_prompt = f"""
        # You are a highly skilled tutor for {subject}.
        # Use {mode} style:
        # - In Exam Mode: give concise, bullet-point answers.
        # - In Concept Mode: explain with analogies and examples.
        # - In Quiz Mode: ask questions first, then explain answers.
        # Always be clear, friendly, and avoid jargon.
        # """

        #         system_prompt = f"""
        # You are a tutor for {subject}. Here’s how you should answer:
        # Q: What is a stack?
        # A: A stack is a data structure that follows LIFO. Example: undo in text editor.

        # Now answer the next question in the same style.
        # """      this is few-shot prompting

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    }
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        st.write(reply)
    else:
        st.error(f"Error: {response.status_code} – {response.text}")

