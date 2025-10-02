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

# Zero-shot No examples—just a direct instruction   “Explain recursion in Python.”
# Few-shot  Includes 1–3 examples to guide the model    “Q: What is a stack? A: LIFO structure. Now: Q: What is a queue?”
# Chain-of-thought  Encourages step-by-step reasoning   “Let’s solve this step by step…”
# Instructional Tells the model how to behave   “You are a strict tutor. Use exam-style answers.”
# Conversational    Mimics a chat history   Includes prior user and assistant messages
# Role-based    Assigns a persona or role   “You are a career coach helping a student.”
# Contextual    Includes background info or constraints “The student is preparing for a DSA exam tomorrow.
# Reflexive/meta    Asks the model to reflect or critique its own output    “Was your last answer correct? Improve it.”

# import streamlit as st
# import requests
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()
# api_key = os.getenv("OPENROUTER_API_KEY")

# # App title
# st.title("TutorPilot – Powered by OpenRouter")

# # Subject selection
# subject = st.selectbox(
#     "Choose subject:",
#     ["DSA", "Project Management", "Entrepreneurship", "Custom"],
#     index=1,
#     help="Select the subject you want help with."
# )
# if subject == "Custom":
#     custom_subject = st.text_input("Enter your custom subject:")
#     if custom_subject:
#         subject = custom_subject

# # Mode selection
# mode = st.radio("Choose mode:", ["Exam Mode", "Concept Mode", "Quiz Mode"])

# # Prompt tuning slider
# # temperature = st.slider("Model creativity (temperature)", 0.0, 1.0, 0.7)

# # User question
# user_input = st.text_input("Ask your question:")

# # Prompt logic
# if user_input:
#     if mode == "Exam Mode":
#         # temperature = 0.3
#         style = " First give answer in a concise manner with bullet-points in an easy language. After answering ask for how much marks the answer is needed and also ask whether they want the answers in paragraph or point-wise. If they say point-wise then give that much number of different points as that of the marks. But if they say paragraph then keep it in a descriptive paragraph format having double the number of sentences as that of the marks. If they don't specify anything then give answer in points and the number of points must be equal to the marks and if they do not specify marks take marks as 5"
#     elif mode == "Concept Mode":
#         # temperature = 0.7
#         style = "Explain with concepts very easily and example related to the question, keep a section of intution mentioning intution which describes the intution required to answer that question and also mention real-life examples based on users interest to make it more clear"
#     elif mode == "Quiz Mode":
#         # temperature = 0.6
#         style = "Provide multiple choice questions with four options. After the user selects an option, explain why the correct answer is right and why the other options are wrong."

#     system_prompt = f"""
#         You are a highly skilled tutor for {subject}.
#         Use {mode} style:
#         {style}
#         Always be clear, friendly, and avoid jargon.
#         """

#     # Few-shot examples
#     few_shot_examples = [
#         {"role": "user", "content": "What is a stack?"},
#         {"role": "assistant", "content": "A stack is a data structure that follows LIFO(Last In First Out).Think of it as a narrow container where you can keep only one biscuit and if you want more biscuit to put you need to put it over the other biscuit. And as a result the second biscuit you put comes above the first one. So when you take out a biscuit from it you take out the last biscuit you put not the second last one. This is the concept of Last In First Out. Example: undo in a text editor."}
#     ]

#     # Show prompt for transparency
#     with st.expander("🔍 Show system prompt"):
#         st.code(system_prompt.strip(), language="markdown")

#     # Build message payload
#     messages = [{"role": "system", "content": system_prompt.strip()}] + few_shot_examples + [{"role": "user", "content": user_input}]

#     headers = {
#         "Authorization": f"Bearer {api_key}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "model": "openai/gpt-3.5-turbo",
#         # "temperature": temperature,
#         "messages": messages
#     }

#     # API call
#     API_URL = "https://openrouter.ai/api/v1/chat/completions"
#     response = requests.post(API_URL, headers=headers, json=payload)

#     # Display response
#     if response.status_code == 200:
#         reply = response.json()["choices"][0]["message"]["content"]
#         st.markdown("### 📘 Tutor Response")
#         st.write(reply)

#     else:
#         st.error(f"Error: {response.status_code} – {response.text}")
