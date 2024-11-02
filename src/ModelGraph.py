import os
import asyncio
from typing import Annotated, Dict, Optional, TypedDict
from typing_extensions import TypedDict
import uuid

import streamlit as st

from langchain.agents import AgentExecutor
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages, AnyMessage
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda

from Assistant import Assistant
import Tools

import datetime

def _print_event(event: dict, _printed: set, max_length=1500):
    current_state = event.get("dialog_state")
    if current_state:
        print("Currently in: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... (truncated)"
            print(msg_repr)
            _printed.add(message.id)

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

class MyGraph():
    def __init__(self, model_name="PersonalGPT"):
        self.model_name = model_name
        self.build_state_graph()

    def build_state_graph(self):
        workflow = StateGraph(MessagesState)

        self.assistant = Assistant()
        workflow.add_node("assistant", self.assistant.__call__)
        workflow.add_node("tools", Tools.create_tool_node_with_fallback())
        
        workflow.add_edge(START, "assistant")
        workflow.add_conditional_edges("assistant", should_continue, ["tools", END])
        workflow.add_edge("tools", "assistant")

        memory = MemorySaver()

        self.config = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
            }
        }

        self.graph = workflow.compile(checkpointer=memory)

    def update_convo(self):
        # Display conversation history
        with self.history_container.container():
            for user_msg, bot_msg in st.session_state.chat_history:
                st.markdown("---")
                st.write(f"**You:** {user_msg}")
                st.write(f"**{self.model_name}:** {bot_msg}")

    def call(self, user_input):
        _printed = set()
   
        state = {"messages": [
            SystemMessage(content=f"You are a helpful assistant. Given a prompt, either answer it directly or use tools as needed.\nCurrent time: {datetime.datetime.now}.\n"), 
            HumanMessage(content=user_input),
        ]}

        print("--->", "CALL INIT", user_input)
        for event in self.graph.stream(
            state,
            stream_mode="values",
            config=self.config
        ):
            print("--->", "Event Called")
            _print_event(event, _printed)

    def call_model_old(self, user_input):
        print("MY GRAPH CALL ----------------------------------------------")
        self.container_text = ""
        st.session_state.chat_history.insert(0, [user_input, self.container_text])

        # Prepare messages directly without wrapping in a dict
        messages = [
            SystemMessage(content="You are a helpful assistant. Use your tools if necessary to generate a response. Use the tool response in your output."),
            HumanMessage(content=user_input),
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
        stream = self.model.stream(messages)
        
        currentstate = None
        for chunk in stream:
            if currentstate:
                currentstate += chunk
            else:
                currentstate = chunk

            print("chunk", chunk.content)
            

        # Clear out response container and finalize conversation
        self.response_container.empty()
        self.update_convo()



