import os
import streamlit as st
from langchain import OpenAI, ConversationChain
from langchain.chains import SimpleSequentialChain

# Initialize the LLM with OpenAI
api_key = st.secrets["OPENAI_API_KEY"]
llm = OpenAI(api_key=api_key)  # Replace with your API key
conversation = ConversationChain(llm=llm)

# Streamlit app layout
st.title("AI Assistant")
st.write("This assistant can perform the following actions:")
st.write("- Write and send emails on your behalf")
st.write("- Read multiple PDF files and answer questions")
st.write("- Schedule meetings for you")
st.write("- Search the Internet")
st.write("- Ask you questions, e.g., for your private information or when uncertain")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("Type your query:")

if st.button("Send") and user_input:
    # Get response from LLM
    response = conversation.run(input=user_input)
    # Append to session history
    st.session_state.chat_history.append((user_input, response))

# Display conversation history
for user_msg, bot_msg in st.session_state.chat_history:
    st.write(f"**You:** {user_msg}")
    st.write(f"**ChatGPT:** {bot_msg}")
