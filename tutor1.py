import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

st.set_page_config(page_title="TutorPilot", layout="centered")
#Add Font Import to Your App
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    * {
        font-family: 'Inter', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("TutorPilot – AI Exam Tutor")

# Subject and mode selection
subject = st.selectbox("Choose subject:", ["DSA", "Project Management", "Entrepreneurship", "Custom"], index=1)
if subject == "Custom":
    custom_subject = st.text_input("Enter your custom subject:")
    if custom_subject:
        subject = custom_subject

mode = st.radio("Choose mode:", ["Exam Mode", "Concept Mode", "Quiz Mode"])

# Prompt logic
if mode == "Exam Mode":
    style = " First give answer in a concise manner with bullet-points in an easy language. After answering ask for how much marks the answer is needed and also ask whether they want the answers in paragraph or point-wise. If they say point-wise then give that much number of different points as that of the marks. But if they say paragraph then keep it in a descriptive paragraph format having double the number of sentences as that of the marks. If they don't specify anything then give answer in points and the number of points must be equal to the marks and if they do not specify marks take marks as 5"
elif mode == "Concept Mode":
    style = "Explain with concepts very easily and example related to the question, keep a section of intution mentioning intution which describes the intution required to answer that question and also mention real-life examples based on users interest to make it more clear"
elif mode == "Quiz Mode":
    style = "Provide multiple choice questions with four options. After the user selects an option, explain why the correct answer is right and why the other options are wrong."

system_prompt = f"You are a highly skilled tutor for {subject}. Use {mode} style: {style} Always be clear, friendly, and avoid jargon."

# Show system prompt for transparency
with st.expander("🔍 Show system prompt"):
    st.code(system_prompt.strip(), language="markdown")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

import re

def markdown_to_html_list(text):
    lines = text.strip().split("\n")
    html_lines = []
    in_list = False

    for line in lines:
        if line.startswith("- "):
            if not in_list:
                html_lines.append("<ul style='padding-left: 20px; margin: 0;'>")
                in_list = True
            html_lines.append(f"<li>{line[2:].strip()}</li>")
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{line.strip()}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)

# Chat input
user_input = st.chat_input("Ask your question...")

if user_input:
    # Build message list
    messages = [{"role": "system", "content": system_prompt}] + st.session_state.chat_history + [{"role": "user", "content": user_input}]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": messages
    }

    # Get assistant reply with spinner
    with st.spinner("TutorPilot is typing..."):
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
        else:
            reply = f"Error: {response.status_code} – {response.text}"
        time.sleep(1.5)

    # Update chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    reply = markdown_to_html_list(reply)
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

# Custom left-right chat layout with themed colors
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"""
            <div style='text-align: right; background-color:#E6F2FF; padding:12px; border-radius:12px; margin:6px 0; width: fit-content; max-width:80%; margin-left:auto; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <span style='font-size:16px; color:#2A2A2A; line-height:1.6; font-weight:500;'>{msg["content"]}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='text-align: left; background-color:#FFFBEA; padding:12px; border-radius:12px; margin:6px 0; width: fit-content; max-width:80%; margin-right:auto; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size:16px; color:#2A2A2A; line-height:1.6; font-weight:500;'>
                <div style='font-size:13px; font-weight:600; color:#555; margin-bottom:6px;'>📌 {mode}</div>
                {msg["content"]}
            </div>
        """, unsafe_allow_html=True)



# Optional: Clear chat
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history = []