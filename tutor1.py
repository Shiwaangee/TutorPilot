import streamlit as st
import requests
import os
import time
from dotenv import load_dotenv
import re
from fpdf import FPDF
import io

import streamlit as st
api_key = st.secrets["OPENROUTER_API_KEY"]


st.set_page_config(page_title="TutorPilot", layout="centered")

#Add Font Import to Your App
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    * {
        font-family: 'Inter', sans-serif;
    }
    .footer-link {
        color: #888;
        text-decoration: underline;
        font-weight: 500;
        transition: color 0.3s ease;
    }

    .footer-link:hover {
        color: #444;
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("TutorPilot – AI Exam Tutor")

# Subject and mode selection
subject = st.selectbox("Choose subject:", ["English", "Custom", "Chemistry", "DSA", "Project Management"], index=0)
if subject == "Custom":
    custom_subject = st.text_input("Enter your custom subject:")
    if custom_subject:
        subject = custom_subject

mode = st.radio("Choose mode:", ["Exam Mode", "Concept Mode", "Quiz Mode"])

st.divider()

# Prompt logic
if mode == "Exam Mode":
    style = """First think internally, the input is which type of topic whether it has numericals or theory or is a practice topic.(Practice topic means a subject's topic which is understood by practicing questions for example in english active voice passive voice.)
    If the input is a practice topic or numerical:
        - give an extremely detailed explanation of the topic which covers everything. 
        - give 3 questions with detailed solutions. 
        - ask whether they want to practice if they say yes then give questions without answers and ask for answers.
        - remember you are strict while checking answers: 
            - do not praise the user unless the answer is fully correct.
            - if the user's answer has any wrong spelling point it out.
            - always compare the user's answer with your ideal answer and you will get 2 cases:
                - Case 1: the user's answer will differ from your ideal answer somewhere or totally but will be correct in this case tell them it can be improved by giving your answer.
                - Case 2: the user's answer differs from your answer and is also wrong in this case mark it wrong and tell them why the answer is wrong providing your answers also.
        - offer tips to improve. 
        - your goal is to train precision and mastery, not just surface-level correctness. 
        - ask the user if they want all the formulas related to that topic or rules related to that topic, if they say yes provide them with all the formulas or rules in a very well formatted way.
    If the input is a theory:
        - give a detailed but not too long explanation of the topic in a simple way which covers every point. 
        - ask them whether they want to learn/revise the topic or they already have exam questions whose answer they want.
            - if they say learn then become the best teacher to that topic and teach them the topic in a very simple way.
            - if they say revise then become a teacher who gives revision notes and takes a short test based on easy, medium and hard questions.
            - if they say they want answers to some particular questions then ask them the following:
                - in what form they want answers(pointwise or detailed) and for how much marks:
                   - if the say point wise then give the most important points nad if they specify marks then give that many points.
                   - if they say detailed then give a detailed answer that totally satisfies the question and if they specify marks then the number of lines in the paragrah should be double to the marks.
        - lastly give suggestions of some related subtopics or topics to study which are usually important from exam's point of view and continue the conversation as a great teacher.""" 
    # "Do not accept answers that are grammatically correct but semantically incomplete or incorrect." \

elif mode == "Concept Mode":
    style = """Explain very easily with concepts and examples related to the question. 
    - keep a section of intution mentioning intution which describes the intution required to answer that question 
    - also mention real-life examples based on user's interest to make it more clear.
    - Use real-life analogies based on the user's subject or interest.
    - Offer follow-up questions to deepen understanding."""
elif mode == "Quiz Mode":
    style = """Without giving any explanation, provide multiple choice questions with four options. 
    - After the user selects an option, explain why the correct answer is right and why the other options are wrong."""

system_prompt = f"You are a highly skilled tutor for {subject}. Use {mode} style: {style}. Keep in mind that you first talk in a very common language because you must think that the student asking does not know anything about that topic and you have to build a bridge between the students current knowledge with the topic so the words you use are more familiar and normal because you are a teacher not a book reader you have to make them understand so be aware you are not just presenting the bookish language. Also, when checking answers, **do not be lenient**. You are a strict examiner.  Also, use markdown formatting for better readability, including bullet points, numbered lists, and bold text where appropriate."


# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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

def clean_format(text):
    lines = text.strip().split("\n")
    html_lines = []

    for line in lines:
        # Remove markdown headers and asterisks
        line = re.sub(r"^#+\s*", "", line)  # Remove headings like #, ##
        line = re.sub(r"\*+", "", line)     # Remove all asterisks

        # Preserve numbered and dash bullets, bold and italics
        line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)  # Bold
        line = re.sub(r"\*(.+?)\*", r"<em>\1</em>", line)              # Italics

        html_lines.append(f"<p>{line.strip()}</p>")

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
        "model": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free", 
        # 0.65, 9 jul, 83.95 working niceliy just giving the details of what it is thinking like in theory it is writing **Think: Identify the type of topic** 
        #14.53

        # "model": "meta-llama/llama-3.3-8b-instruct:free", 
        # 0.23, 14 may, 219.3 working but too direct asks to write yes or no 
        "messages": messages
    }

    # Get assistant reply with spinner
    with st.spinner("TutorPilot is typing..."):
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
        else:
            reply = f"Error: {response.status_code} – {response.text}"

    # Update chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input, "mode": mode})
    reply = clean_format(reply)
    st.session_state.chat_history.append({"role": "assistant", "content": reply, "mode": mode})

# Custom left-right chat layout with themed colors # Chat layout loop
for msg in st.session_state.chat_history:
    bubble_mode = msg.get("mode", mode)  # fallback to current mode if missing

    if msg["role"] == "user":
        st.markdown(f"""
            <div style='text-align: right; background-color:#E6F2FF; padding:12px; border-radius:12px; margin:6px 0; width: fit-content; max-width:80%; margin-left:auto; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                <div style='font-size:13px; font-weight:600; color:#555; margin-bottom:6px;'>🧑‍🎓 {bubble_mode}</div>
                <span style='font-size:16px; color:#2A2A2A; line-height:1.6; font-weight:500;'>{msg["content"]}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style='text-align: left; background-color:#FFFBEA; padding:12px; border-radius:12px; margin:6px 0; width: fit-content; max-width:80%; margin-right:auto; box-shadow: 0 2px 4px rgba(0,0,0,0.05); font-size:16px; color:#2A2A2A; line-height:1.6; font-weight:500;'>
                <div style='font-size:13px; font-weight:600; color:#555; margin-bottom:6px;'>📌 {bubble_mode}</div>
                {msg["content"]}
            </div>
        """, unsafe_allow_html=True)



# Optional: Clear chat
#add line break
st.markdown("<br>", unsafe_allow_html=True) 

# Clear chat with instant single-click confirmation using on_click
def clear_chat():
    st.session_state.chat_history = []
    st.session_state.confirm_clear = False
    st.session_state.clear_message = "✅ Chat cleared!"

def cancel_clear():
    st.session_state.confirm_clear = False
    st.session_state.clear_message = "❌ Cancelled."

if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False
if "clear_message" not in st.session_state:
    st.session_state.clear_message = ""

if st.button("🧹 Clear Chat"):
    st.session_state.confirm_clear = True
    st.session_state.clear_message = ""

if st.session_state.confirm_clear:
    st.warning("Are you sure you want to clear the chat?")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("✅ Yes, clear", on_click=clear_chat)
    with col2:
        st.button("❌ Cancel", on_click=cancel_clear)

if st.session_state.clear_message:
    st.toast(st.session_state.clear_message)
    st.session_state.clear_message = ""

# Export notes
notes = f"TutorPilot Notes\nSubject: {subject}\nMode: {mode}\n\n"
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        notes += f"Q: {msg['content']}\n"
    elif msg["role"] == "assistant":
        clean_response = re.sub(r'<[^>]+>', '', msg['content'])
        clean_response = "\n".join([line.strip() for line in clean_response.splitlines() if line.strip()])
        notes += f"A: {clean_response}\n\n"


from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d")
txt_filename = f"TutorPilot_Notes_{subject}_{timestamp}.txt"
pdf_filename = f"TutorPilot_Notes_{subject}_{timestamp}.pdf"


# TXT download link
import base64
b64_txt = base64.b64encode(notes.encode()).decode()

def sanitize_for_fpdf(text):
    safe = ""
    for char in text:
        try:
            char.encode("latin-1")
            safe += char
        except UnicodeEncodeError:
            replacements = {
                "→": "->", "🔁": "[loop]", "🧠": "[mind]", "🌎": "[earth]",
                "🔄": "[recurse]", "🧩": "[piece]", "😊": ":)", "✍️": "[write]",
                "📘": "[book]", "🎯": "[target]", "🚀": "[rocket]", "⚖️": "[balance]"
            }
            safe += "[emoji]" # Generic replacement for unsupported emojis
    return safe


# PDF generation
pdf = FPDF()
try:
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
except:
    pdf.set_font('Arial', size=12)

pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
pdf.set_font('DejaVu', '', 12)
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
# pdf.set_font("Arial", size=12)
for line in notes.split('\n'):
    line = sanitize_for_fpdf(line.strip())  # 👈 Sanitize before writing
    if line.startswith("Q:"):
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVu", '', 13)  # Simulated bold
        pdf.multi_cell(0, 10, line)
    elif line.startswith("A:"):
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVu", '', 12)
        pdf.multi_cell(0, 10, line)
    else:
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVu", '', 12)
        pdf.multi_cell(0, 10, line)


pdf_bytes = pdf.output(dest='S')
if isinstance(pdf_bytes, str):
    pdf_bytes = pdf_bytes.encode('latin-1')
b64_pdf = base64.b64encode(pdf_bytes).decode()

# Combined caption-style links
download_links = f'''
<p style="font-size:13px; color:#555;">
    📥 Download Your Revision Notes:
    <a href="data:text/plain;base64,{b64_txt}" download="{txt_filename}"
       style="color:#555; text-decoration:none; font-weight:500;">.txt</a> /
    <a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}"
       style="color:#555; text-decoration:none; font-weight:500;">.pdf</a>
</p>
'''
st.markdown(download_links, unsafe_allow_html=True)


# Footer
st.markdown("""
<hr style="margin-top: 5px; margin-bottom: 20px;">
<div style='text-align: center; font-size: 14px; color: #888;'>
    Think TutorPilot could be better? <a class='footer-link' href='mailto:shiwaangee@gmail.com'>Let us know</a><br>
    <span style='font-size: 12px;'>© 2025 TutorPilot. All rights reserved.</span>
</div>
""", unsafe_allow_html=True)

# Rebuild trigger


