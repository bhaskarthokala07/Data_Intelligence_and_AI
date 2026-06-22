
import streamlit as st
from groq import Groq
from weather_api import get_weather_with_forecast
from prompt_builder import build_weather_prompt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Streamlit Page Config
st.set_page_config(
    page_title="AI Weather Chatbot",
    page_icon="🌤️",
    layout="centered"
)

st.title("🌤️ AI Weather Chatbot (Groq Powered)")
st.write("Get live weather information and ask AI weather-related questions.")

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "weather_data" not in st.session_state:
    st.session_state.weather_data = None

if "city" not in st.session_state:
    st.session_state.city = ""

if "questions_left" not in st.session_state:
    st.session_state.questions_left = 5

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    default_key = os.getenv("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", "")

    groq_key = st.text_input(
        "Groq API Key",
        value=default_key,
        type="password"
    )

    st.markdown("---")

    if st.button("🔄 Reset Chat"):
        st.session_state.chat_history = []
        st.session_state.weather_data = None
        st.session_state.city = ""
        st.session_state.questions_left = 5
        st.rerun()

# Main Application
if st.session_state.questions_left > 0:

    # Weather Fetch Mode
    if not st.session_state.weather_data:

        city = st.text_input(
            "Enter City Name",
            value="Hyderabad"
        )

        if st.button("🌤️ Get Weather & Start Chat"):

            if not groq_key:
                st.error("Please enter your Groq API Key.")
            else:
                with st.spinner("Fetching weather data..."):

                    weather = get_weather_with_forecast(city)

                if "error" in weather:
                    st.error(weather["error"])

                else:
                    st.session_state.weather_data = weather
                    st.session_state.city = city
                    st.rerun()

    # Chat Mode
    else:

        st.success(
            f"📍 City: {st.session_state.city} | "
            f"Questions Left: {st.session_state.questions_left}"
        )

        user_question = st.text_input(
            "Ask a weather-related question:"
        )

        if st.button("Send") and user_question:

            prompt = build_weather_prompt(
                weather_data=st.session_state.weather_data,
                user_question=user_question,
                chat_history=st.session_state.chat_history
            )

            try:
                client = Groq(
                    api_key=groq_key
                )

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a professional weather assistant. "
                                "Answer weather-related questions clearly "
                                "using the provided weather data."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=500
                )

                answer = response.choices[0].message.content

                # Save Chat History
                st.session_state.chat_history.append(
                    (user_question, answer)
                )

                st.session_state.questions_left -= 1

                st.rerun()

            except Exception as e:
                st.error(f"Groq API Error: {str(e)}")

        # Display Chat History
        st.markdown("## 💬 Chat History")

        for q, a in st.session_state.chat_history:

            with st.chat_message("user"):
                st.write(q)

            with st.chat_message("assistant"):
                st.write(a)

# Question Limit Reached
else:

    st.warning(
        "⚠️ You have reached the 5-question limit for this city."
    )

    if st.button("Start New City"):

        st.session_state.chat_history = []
        st.session_state.weather_data = None
        st.session_state.city = ""
        st.session_state.questions_left = 5

        st.rerun()
