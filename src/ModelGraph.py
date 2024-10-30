import os
import streamlit as st
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain.agents import AgentExecutor
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from typing import Dict, TypedDict, Optional
from langchain_core.runnables import RunnableConfig

@tool
def calculator_adder(num1: float, num2: float) -> float:
    '''Return the sum of 2 numbers'''
    return num1 + num2

@tool
def calculator_multiplier(num1: float, num2: float) -> float:
    '''Return the product of 2 numbers'''
    return num1 * num2

@tool
def calculator_exponent(base: float, exponent: float) -> float:
    '''Return the exponentiation of the "base" to the power of "exponent"'''
    return base ** exponent

tools = [calculator_adder, calculator_exponent, calculator_multiplier]

class GraphState(TypedDict):
    question: Optional[str] = None

class MyGraph():
    def __init__(self, model, history_container, response_container):
        self.workflow = StateGraph(GraphState)
        self.history_container = history_container
        self.response_container = response_container
        self.model = model
        self.model_name = "PersonalGPT"
        self.app = create_react_agent(model=self.model, tools=tools)

        self.container_text = ''

    def update_convo(self):
        # Display conversation history
        with self.history_container.container():
            for user_msg, bot_msg in st.session_state.chat_history:
                st.markdown("---")
                st.write(f"**You:** {user_msg}")
                st.write(f"**{self.model_name}:** {bot_msg}")

    def call(self, user_input):
        print("MY GRAPH CALL ----------------------------------------------")
        self.container_text = ""
        st.session_state.chat_history.insert(0, [user_input, self.container_text])

        # Prepare messages directly without wrapping in a dict
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=user_input)
        ]
        inputs = {
            "messages": messages
        }
        
        # Initial display before streaming starts
        self.response_container.markdown(
            f"**You:** {user_input}\n\n**{self.model_name}:** Thinking..."
        )

        # Config setup for compatibility with streaming
        config = RunnableConfig(configurable={"thread_id": "agent_1"})

        # Synchronously handle events by iterating through them
        stream = self.app.stream(inputs, config=config)
        for chunk in stream:
            if not st.session_state.is_generating:
                break  # Stop if is_generating is set to False

            print("new chunk", chunk)

        # Clear out response container and finalize conversation
        self.response_container.empty()
        self.update_convo()



