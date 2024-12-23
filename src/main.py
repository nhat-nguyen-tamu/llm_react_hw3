import os
import streamlit as st
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_core.tools import tool

from ModelGraph import AgentGraph

# Streamlit app layout
st.title("CSCE 689 Programming LLMs: Chat Assistant")
st.write("This assistant can perform the following actions:")
st.write("- Write and send emails on your behalf")
#st.write("- Read multiple PDF files and answer questions")
st.write("- Schedule meetings for you")
st.write("- Search the Internet")
st.write("- Ask you questions, e.g., for your private information or when uncertain")

# Callback to handle event updates
def tostring_event(event):
    if event.get('user'):
        return f"**You:** {event['user']}"
    elif event.get('assistant'):
        return f"**{st.session_state.my_graph.model_name}:** {event['assistant']}"
    elif event.get('tool_call'):
        call_output = ["**Tool Calls:**"]
        for call_instance in event['tool_call']:
            call_output.append(f"\t{call_instance['name']}: {str(call_instance['args'])}")

        return '\n\n'.join(call_output)
    elif event.get('tool_response'):
        return event['tool_response']

    return event

def event_callback(event):
    print("---> event callback", event)
    st.session_state.response_text = f"{st.session_state.response_text}\n\n{tostring_event(event)}" # read from top down
    # st.session_state.response_text = f"{tostring_event(event)}\n\n{st.session_state.response_text}" # read from bottom up
    response_container.markdown(f"{st.session_state.response_text}")

# Callback to handle streaming text
def stream_callback(text_chunk):
    pass

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "confirmations" not in st.session_state:
    st.session_state.confirmations = []

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

if "response_text" not in st.session_state:
    st.session_state.response_text = ""

if "my_graph" not in st.session_state:
    st.session_state.my_graph = AgentGraph(model_name="PersonalGPT", event_callback=event_callback, stream_callback=stream_callback)

# Form for user input and button
with st.form(key="chat_form"):
    user_input = st.text_input("Type your query:")
    submit_button = st.form_submit_button("Send")

response_container = st.empty()
st.markdown("---")
history_container = st.empty()

def update_history():
    if True: # CONFIGURABLE BLOCK: if you turn off LLM memory, you can enable chat history, otherwise it just repeats itself, very messy
        return

    # Update chat history
    with history_container.container():
        for message_block in reversed(st.session_state.chat_history):
            st.markdown(f"{message_block}")
            st.markdown("---")

def empty_response_container():
    st.session_state.response_text = ""
    response_container.empty()

def submit_response_to_history():
    if True: # CONFIGURABLE BLOCK: if you turn off LLM memory, you can enable chat history, otherwise it just repeats itself, very messy
        return
    st.session_state.chat_history.append(st.session_state.response_text)
    empty_response_container()
    update_history()

update_history()

if st.session_state.confirmations:
    action = st.session_state.confirmations[0]
    
    @st.dialog("LLM Tool Confirmation")
    def confirmation(action):
        st.write(f"Allow the LLM to run this action?\n\n{action}")

        left, right = st.columns(2)
        if left.button("Submit", use_container_width=True):
            st.session_state.confirmations.pop()
            action['function'](*action['args'], **action['kwargs'])
            st.rerun()
        elif right.button("Cancel", use_container_width=True):
            st.session_state.confirmations.pop()
            st.rerun()
    
    confirmation(action['message'])


if submit_button and user_input:
    if st.session_state.is_generating:
        st.session_state.my_graph.abort()
        st.session_state.is_generating = False
    else:
        # Set the flag to indicate that the model is generating text
        st.session_state.is_generating = True
        empty_response_container()

        st.session_state.my_graph.call(user_input)
        submit_response_to_history()

        st.session_state.is_generating = False