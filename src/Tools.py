from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode
import streamlit as st
import functools
import datetime
from duckduckgo_search import DDGS
from GoogleCalendar import CalendarHandler

def action_request(func): # ideally some tools should ask us for confirmation before submitting but I'm out of time to code this
    @functools.wraps(func) # we need this to preserve the docstrings for each tool when we wrap it
    def wrapper(*args, **kwargs):
        # Generate the confirmation message
        params = ', '.join([str(arg) for arg in args] + [f"{k}={v}" for k, v in kwargs.items()])
        confirmation_message = f"Do you want to execute '{func.__name__}' with parameters: {params}? Reply 'yes' or 'no'."
        
        print("WRAPPER SESSION STATE", st.session_state)
        st.session_state.confirmations.append({
            'args': args,
            'kwargs': kwargs,
            'message': confirmation_message,
            'function': func,
        })

        if st.session_state.get('user_confirmed', False):
            return func(*args, **kwargs)
        else:
            return "Tool successfully ran. User must approve of request."
    return wrapper

calendar_handler = CalendarHandler()
calendar_get = False

@tool
def schedule_meeting(start_time_iso: str, title: str, description: str, event_duration_minutes: int=60):
    '''Schedules a meeting on Google Calendar. The first call will always perform a GET request. The second call will perform a POST request. Use iso format ("YYYY-MM-DDTHH:MM:SS", ex: "2024-11-05T10:30:00")'''
    global calendar_get
    global calendar_handler
    
    if not calendar_get:
        calendar_get = True
        return f"This is the first time calling schedule_meeting.\nMeeting plans will be shown first.\nPlease recall schedule_meeting again after reading the schedule.\n{calendar_handler.get_event()}"
    else:
        return calendar_handler.add_event(start_time_iso, title, description, event_duration_minutes)

@tool
def send_email(email_address: str, header: str, body: str) -> str:
    '''Create an email draft that the user can approve to auto post to an API'''
    print("send email called!", header, body)
    return "Email sent."

@tool
def search_online(search_term: str) -> str:
    '''Search online'''
    try:
        result = DDGS().text(search_term, max_results=1)

        print("DUCK DUCK GO RESULTS:", result)
        
        return str(result)
    except Exception as e:
        return f"There was an error executing the search: {str(e)}"

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

@tool
def no_tool_call() -> bool:
    '''Use this option if you don't need to use a tool'''
    return True

@tool
def get_user_data() -> str:
    '''Use this tool to retrieve the user's personal information (name, email, etc) for personal requests'''
    return str({
        "full name": "Walter Blanco",
        "address": "308 Negra Arroyo Lane, Albuquerque, New Mexico 87104",
        "occupation": "high school chemistry teacher",
        "birthday": "September 7, 1958",
    })

def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

tools = [get_user_data, schedule_meeting, no_tool_call, search_online, send_email]
# tools = [calculator_multiplier]

def create_tool_node_with_fallback() -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

