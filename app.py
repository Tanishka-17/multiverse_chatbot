import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

avatars = {
    "An expert Hacker": "💻",
    "Ironman": "🚀",
    "An angry Ravi Shastri": "🏏",
    "A crazy Ronaldo fan": "⚽",
    "user": "👤"
}

if "histories" not in st.session_state:
    st.session_state.histories = {}

personality = st.sidebar.selectbox(
    "Who do you want to talk to?",
    ["An expert Hacker", "Ironman", "An angry Ravi Shastri", "A crazy Ronaldo fan"]
)

if personality not in st.session_state.histories:
    st.session_state.histories[personality] = []

current_history = st.session_state.histories[personality]
intensity = st.sidebar.slider("Intensity", min_value=1, max_value=10, value=5)

if "last_tokens" not in st.session_state:
    st.session_state.last_tokens = 0

if st.session_state.last_tokens > 0:
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 System Check: Your last message was roughly **{st.session_state.last_tokens:.1f}** tokens.")

st.sidebar.markdown("---")
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.histories[personality] = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("🚀 Built by Tanishka")
st.sidebar.caption("[View Source Code](https://github.com/Tanishka-17/multiverse-chatbot)")

if len(current_history) == 0:
    st.title("The MULTIVERSE OF CHATBOTS")
    st.info(f"Welcome to the void. Send a message to summon **{personality}**.")
else:
    st.title(f"Chatting with: {personality} {avatars[personality]}")
    st.caption(f"Emotional Intensity: {intensity}/10")

if not api_key:
    st.error("Please add your GEMINI_API_KEY to your .env file!")
    st.stop()

client = genai.Client(api_key=api_key)

for message in current_history:
    display_avatar = avatars["user"] if message["role"] == "user" else avatars[personality]
    with st.chat_message(message["role"], avatar=display_avatar):
        st.markdown(message["content"])

if user_prompt := st.chat_input(f"Send a message to {personality}..."):
    
    st.session_state.last_tokens = len(user_prompt) / 4
    
    with st.chat_message("user", avatar=avatars["user"]):
        st.markdown(user_prompt)
    current_history.append({"role": "user", "content": user_prompt})

    sys_instruction = (
        f"You are strictly playing the role of: {personality}. "
        f"Your current emotional intensity/passion level is {intensity} out of 10. "
        "Adjust your tone, enthusiasm, punctuation, and vocabulary to match this character and intensity exactly."
    )

    api_history = []
    for msg in current_history[:-1]: 
        api_history.append(
            types.Content(
                role="user" if msg["role"] == "user" else "model",
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    with st.chat_message("assistant", avatar=avatars[personality]):
        try:
            chat = client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=sys_instruction,
                    temperature=0.6 + (intensity * 0.04) 
                ),
                history=api_history
            )
            
            response = chat.send_message(user_prompt)
            st.markdown(response.text)
            
            current_history.append({"role": "assistant", "content": response.text})
            st.rerun()
                
        except Exception as e:
            st.error(f"API Error: {e}")