import os
import json
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as gen_ai


# Load environment variables
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="Chat with Gemini-Pro!",
    page_icon=":brain:",  # Favicon emoji
    layout="centered",  # Page layout option
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up Google Gemini-Pro AI model
gen_ai.configure(api_key=GOOGLE_API_KEY)
model = gen_ai.GenerativeModel('gemini-2.0-flash')


# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# Add these functions after the imports
def save_chat_history(history):
    """Save chat history to data.txt"""
    chat_data = []
    for message in history:
        chat_data.append({
            "role": message.role,
            "text": message.parts[0].text
        })
    
    with open("data.txt", "w") as f:
        json.dump(chat_data, f)

def load_chat_history():
    """Load chat history from data.txt"""
    try:
        with open("data.txt", "r") as f:
            chat_data = json.load(f)
            
        # Convert saved messages to format expected by Gemini
        history = []
        for message in chat_data:
            if message["role"] == "user":
                history.append({"role": "user", "parts": [message["text"]]})
            else:
                history.append({"role": "model", "parts": [message["text"]]})
        return history
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# Modify the chat session initialization
if "chat_session" not in st.session_state:
    # Load existing history when starting new chat session
    saved_history = load_chat_history()
    st.session_state.chat_session = model.start_chat(history=saved_history)


# Display the chatbot's title on the page
st.title("🤖 Gemini Pro - ChatBot")

# Function to check if the message is about unit conversion
def is_unit_conversion_query(text):
    # List of keywords that might indicate a unit conversion question
    conversion_keywords = [
        'convert', 'conversion', 'to', 
        'meters', 'kilometers', 'miles', 'feet',
        'kilograms', 'pounds', 'grams', 'ounces',
        'celsius', 'fahrenheit', 'kelvin',
        'liters', 'gallons', 'milliliters',
        'hours', 'minutes', 'seconds'
    ]
    
    text_lower = text.lower()
    # Check if any of the keywords are in the text
    return any(keyword in text_lower for keyword in conversion_keywords)

# Display the chat history
for message in st.session_state.chat_session.history:
    with st.chat_message(translate_role_for_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Input field for user's message
user_prompt = st.chat_input("Ask about unit conversions...")
if user_prompt:
    # Add user's message to chat and display it
    st.chat_message("user").markdown(user_prompt)

    # Check if the query is about unit conversion
    if is_unit_conversion_query(user_prompt):
        # Send user's message to Gemini-Pro and get the response
        gemini_response = st.session_state.chat_session.send_message(
            f"Please help with this unit conversion: {user_prompt}. "
            "Only provide the conversion result and nothing else. "
            "If this is not a valid unit conversion request, reply with 'Invalid conversion request.'"
        )

        # Display Gemini-Pro's response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)
            
        # Save updated chat history
        save_chat_history(st.session_state.chat_session.history)
    else:
        # If not a unit conversion question, display a message
        with st.chat_message("assistant"):
            st.markdown("I can only help with unit conversion questions. Please ask me to convert between different units.")
        save_chat_history(st.session_state.chat_session.history)