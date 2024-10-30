import os
import streamlit as st
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

from ModelGraph import MyGraph

# Streamlit app layout
st.title("CSCE 689 Programming LLMs: Chat Assistant")
st.write("This assistant can perform the following actions:")
st.write("- Write and send emails on your behalf")
st.write("- Read multiple PDF files and answer questions")
st.write("- Schedule meetings for you")
st.write("- Search the Internet")
st.write("- Ask you questions, e.g., for your private information or when uncertain")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Flag to track if the model is generating text
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# Create the agent
# memory = MemorySaver()
llama_llm = ChatOllama(model="llama3.2")

# api_key = st.secrets["OPENAI_API_KEY"]
# openai_llm = openai(api_key=api_key)  # Replace with your API key

# Form for user input and button
with st.form(key="chat_form"):
    user_input = st.text_input("Type your query:")
    submit_button = st.form_submit_button("Send")

# Placeholder for the bot response to update during streaming
response_container = st.empty()
st.markdown("---")
history_container = st.empty()

if "my_graph" not in st.session_state:
    st.session_state.my_graph = MyGraph(llama_llm, history_container, response_container)

if submit_button and user_input:
    # If the model is currently generating, stop it
    if st.session_state.is_generating:
        st.session_state.is_generating = False
    else:
        # Set the flag to indicate that the model is generating text
        st.session_state.is_generating = True

        # Get response from LLM
        st.session_state.my_graph.call(user_input)
        print("run finished")

        # Clear generating flag once done or interrupted
        st.session_state.is_generating = False