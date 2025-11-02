################################################################################
# Author: Faaezah Ahmed Shaik
# Grade: 10
# Date: 1st November 2025
# Description: This was aimed to provide students at Vista Ridge High school
# with a better chatbot resource to use a virtual mentor. This was made as
#one of the projects for ML club. The author wishes whoever uses this a warm welcome
# Astra and hopes that one will have an enjoyable experience with it.
################################################################################



import spacy
import random
import os
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from better_profanity import profanity
import openai

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)
CORS(app)


#Dear reader, I apologize for the vast amount of super annoying debugging statements across the code. I am afraid that
# this was terribly necessary to fix the vast amount of errors this code had gotten. Happy reading!
@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        print("Received message from frontend:", data)
        user_input = data.get("message", "")
        reply = chatbot_response(user_input)
        return jsonify({"reply": reply})
    except Exception as e:
        print("❌ Flask crashed:", e)
        return jsonify({"reply": "Oops! Something broke on the server."}), 500

try:
    nlp = spacy.load("en_core_web_md")
except Exception:
    nlp = spacy.load("en_core_web_sm")

profanity.load_censor_words()

def contains_violation(text):
    return profanity.contains_profanity(text)

def extract_intent(text):
    doc = nlp(text)
    action, topic = None, None
    for token in doc:
        if token.dep_ == "ROOT":
            action = token.lemma_
        if token.dep_ in ["dobj", "pobj", "nsubj", "attr"] and token.pos_ == "NOUN":
            topic = token.text
    return {"intent": action, "topic": topic}

def is_about_Study(text):
    keywords = [
        "study", "homework", "assignment", "test", "quiz", "exam", "notes", "review",
        "flashcards", "outline", "summarize", "learn", "memorize", "tutor", "help",
        "explain", "understand", "practice", "strategy", "focus", "motivation",
        "time management", "productivity", "essay", "grammar", "punctuation", "thesis",
        "paragraph", "sentence", "writing", "reading", "literature", "poetry", "novel",
        "analysis", "math", "algebra", "geometry", "calculus", "equation", "formula",
        "solve", "graph", "statistics", "probability", "science", "biology", "chemistry",
        "physics", "experiment", "hypothesis", "cell", "molecule", "energy", "reaction",
        "history", "geography", "civics", "government", "timeline", "war", "revolution",
        "constitution", "map", "culture"
    ]
    return any(word in text.lower() for word in keywords)

def get_Study_Info(query):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Astra, a helpful school assistant."},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print("❌ OpenAI error:", e)
        return "Oops! I had trouble finding an answer. Try again?"

def get_live_quiz(category):
    return "Sorry, I couldn't find a complete answer."

def is_confirmation(text):
    confirmations = ["yes", "yeah", "yep", "sure", "please", "go ahead", "okay", "ok"]
    return text.strip().lower() in confirmations

def random_Study_tip():
    tips = [
        "🪄 Break big tasks into smaller steps to make them less overwhelming.",
        "🪄 Use flashcards to boost memory and reinforce key concepts.",
        "🪄 Study in short, focused sessions — try the Pomodoro technique.",
        "🪄 Teach someone else what you’ve learned to deepen your understanding.",
        "🪄 Take regular brain breaks to stay sharp and avoid burnout.",
    ]
    return random.choice(tips)

def generate_quiz(topic):
    print("Generating quiz for topic:", topic)
    prompt = f"""
    Create a multiple-choice quiz with 3 questions about {topic}.
    Each question should have 4 answer options labeled a), b), c), d).
    Clearly mark the correct answer after each question.
    Format it like this:

    Q1: [question]
    a) Option A
    b) Option B
    c) Option C
    d) Option D
    Answer: [correct option letter]

    Repeat for Q2 and Q3.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print("❌ Error in generate_quiz:", e)
        return "Oops! I had trouble generating your quiz. Try again?"




def chatbot_response(text):
    print("chatbot_response received:", text)
    if "study tip" in text or "tip" in text:
        return f"{random_Study_tip()}"
    if "sorry" in text or "my apologies" in text:
        return f"No problem! How can I help you today?"
    if contains_violation(text):
        return "That message may violate guidelines. Let’s keep things kind and respectful."
    if is_confirmation(text):
        return "Awesome! Try outlining your thoughts or breaking the task into smaller steps."
    if text.strip().lower() in ["stop", "exit", "quit", "bye", "leave me alone"]:
        return "No problem! I’ll be here whenever you need me. Just click 💬 to reopen the chat."

    if any(word in text.lower() for word in ["quiz", "practice question", "test question", "sample problem"]):
        doc = nlp(text)
        topic = None
        for token in doc:
            if token.pos_ == "NOUN":
                topic = token.text
                break
        if topic:
            return generate_quiz(topic)
        else:
            return "I'll be happy to help you but I need you to specify what type of quiz you would like."

    if is_about_Study(text):
        return get_Study_Info(text)

    return get_Study_Info(text)
print("🔑 Testing OpenAI key with GPT-3.5...")
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello"}]
    )
    print("✅ GPT-3.5 response:", response.choices[0].message["content"])
except Exception as e:
    print("❌ GPT-3.5 error:", e)





if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
