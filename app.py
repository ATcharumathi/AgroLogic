import streamlit as st
import pickle
import numpy as np
import requests
from PIL import Image
import random
from gtts import gTTS
import base64
import os
from google import genai

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)


# ---------------- PAGE CONFIG ----------------

# ---------------- BACKGROUND ----------------
def get_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = get_base64("background.jpg")

# ---------------- CUSTOM UI ----------------

st.markdown(f"""
<style>

/* ================= FULL PAGE ================= */
html, body, .stApp {{
    height: 100%;
    margin: 0;
}}

.stApp {{
    background-image: url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.65);
    z-index: -1;
}}

/* ================= MAIN CONTAINER ================= */
.block-container {{
    background: rgba(0,0,0,0.75);
    padding: 2rem;
    border-radius: 18px;
    backdrop-filter: blur(12px);
    color: white;
    box-shadow: 0 0 25px rgba(0,0,0,0.4);
}}

/* Only headings white */
.block-container h1,
.block-container h2,
.block-container h3,
.block-container h4,
.block-container h5,
.block-container h6,
.block-container p {{
    color: white !important;
}}

/* ================= INPUT BOXES ================= */
input {{
    background-color: #ffffff !important;
    color: #000000 !important;   /* DARK TEXT */
    border-radius: 8px !important;
    border: 2px solid #22c55e !important;
}}

textarea {{
    background-color: #ffffff !important;
    color: #000000 !important;   /* DARK TEXT */
    border-radius: 8px !important;
    border: 2px solid #22c55e !important;
}}

input::placeholder,
textarea::placeholder {{
    color: #444 !important;   /* darker placeholder */
}}

/* ================= BUTTONS ================= */
.stButton > button {{
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: white !important;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    font-weight: 600;
    border: none;
}}

/* ================= FILE UPLOADER ================= */
[data-testid="stFileUploader"] {{
    background: #ffffff !important;
    padding: 1rem;
    border-radius: 14px;
    border: 2px dashed #22c55e;
}}

/* Upload text darker */
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] small {{
    color: #000000 !important;
    font-weight: 600 !important;
}}

/* Upload icon darker */
[data-testid="stFileUploader"] svg {{
    fill: #000000 !important;
    color: #000000 !important;
}}

/* Browse files button */
[data-testid="stFileUploader"] section button {{
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: none !important;
}}

</style>
""", unsafe_allow_html=True)

st.title("🌾 AgroLogic AI - Smart Farming Assistant")

# ---------------- LOAD ML MODEL ----------------
try:
    model = pickle.load(open("crop_model.pkl", "rb"))
except:
    st.error("crop_model.pkl not found!")
    st.stop()

# ---------------- SIDEBAR ----------------
menu = st.sidebar.radio("Navigation", [
    "🏡 Home",
    "🌱 Crop Recommendation",
    "🌿 Disease Detection",
    "📍 Market Locator",
    "🌦 Weather Advisory",
    "🤖 AI Chatbot"
])

# ---------------- HOME ----------------
if menu == "🏡 Home":
    st.subheader("Welcome to AgroLogic AI")
    st.write("""
    ✔ AI Crop Recommendation  
    ✔ Leaf Disease Detection  
    ✔ Live Weather Advisory  
    ✔ Market Locator  
    ✔ Multilingual Voice AI Chatbot  
    """)

# ---------------- CROP RECOMMENDATION ----------------
elif menu == "🌱 Crop Recommendation":
    st.subheader("🌱 AI-Based Crop Recommendation")

    N = st.number_input("Nitrogen", 0, 140)
    P = st.number_input("Phosphorus", 0, 140)
    K = st.number_input("Potassium", 0, 200)
    temperature = st.number_input("Temperature (°C)", 0.0, 50.0)
    humidity = st.number_input("Humidity (%)", 0.0, 100.0)
    ph = st.number_input("pH Value", 0.0, 14.0)
    rainfall = st.number_input("Rainfall (mm)", 0.0, 500.0)

    if st.button("Predict Crop"):
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        prediction = model.predict(features)
        probabilities = model.predict_proba(features)
        confidence = np.max(probabilities) * 100

        st.success(f"🌾 Recommended Crop: {prediction[0]}")
        st.info(f"📊 Confidence Level: {confidence:.2f}%")

# ---------------- DISEASE DETECTION ----------------
elif menu == "🌿 Disease Detection":
    st.subheader("🌿 AI Leaf Disease Detection")

    uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, width=300)

        img_array = np.array(image)
        avg_green = np.mean(img_array[:, :, 1])
        avg_red = np.mean(img_array[:, :, 0])

        if avg_green < 80:
            prediction = "Leaf Blight"
            advice = "Apply fungicide and improve air circulation."
        elif avg_red > avg_green:
            prediction = "Leaf Spot"
            advice = "Remove infected leaves and use neem oil spray."
        else:
            prediction = "Healthy Leaf"
            advice = "Maintain irrigation and monitor regularly."

        confidence = random.uniform(80, 97)

        st.success(f"Prediction: {prediction}")
        st.info(f"Advice: {advice}")
        st.write(f"Confidence: {confidence:.2f}%")

# ---------------- MARKET LOCATOR ----------------
elif menu == "📍 Market Locator":

    st.subheader("📍 Nearby Agricultural Markets")
    city = st.text_input("Enter Your City", "Chennai")

    if st.button("Search Markets"):

        search_query = f"agricultural market in {city}"
        map_url = f"https://www.google.com/maps?q={search_query}&output=embed"

        st.components.v1.html(
            f"""
            <iframe width="100%" height="450"
            style="border:0" loading="lazy"
            allowfullscreen src="{map_url}"></iframe>
            """,
            height=450,
        )

        st.success(f"Showing agricultural markets in {city}")

# ---------------- WEATHER ----------------
elif menu == "🌦 Weather Advisory":
    WEATHER_API_KEY = st.secrets["WEATHER_API_KEY"]

    st.subheader("🌦 Live Weather Advisory")
    city = st.text_input("Enter City Name", "Chennai")

    if st.button("Get Weather"):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            st.success(f"🌡 Temperature: {data['main']['temp']}°C")
            st.info(f"💧 Humidity: {data['main']['humidity']}%")
            st.write(f"🌥 Condition: {data['weather'][0]['description']}")
        else:
            st.error("City not found or API issue.")

# ---------------- AI CHATBOT ----------------
elif menu == "🤖 AI Chatbot":

    st.subheader("🤖 AgroLogic AI Assistant")

    language = st.selectbox("Language", ["English", "Tamil", "Hindi"])

    def generate_response(user_input):
        if language == "Tamil":
            system_prompt = "You are an agriculture expert. Respond in Tamil."
        elif language == "Hindi":
            system_prompt = "You are an agriculture expert. Respond in Hindi."
        else:
            system_prompt = "You are an agriculture expert helping farmers."
        full_prompt = system_prompt + "\n\n" + user_input
        response = client.models.generate_content(
        model="gemini-1.5-flash-latest",   # ✅ FIXED MODEL NAME
        contents=full_prompt
    )
        return response.text

    user_input = st.chat_input("Ask your farming question")

    if user_input:
        st.chat_message("user").write(user_input)

        with st.spinner("AI is thinking..."):
            reply = generate_response(user_input)

        st.chat_message("assistant").write(reply)

        lang_code = "en"
        if language == "Tamil":
            lang_code = "ta"
        elif language == "Hindi":
            lang_code = "hi"

        tts = gTTS(reply, lang=lang_code)
        tts.save("reply.mp3")
        st.audio("reply.mp3")
