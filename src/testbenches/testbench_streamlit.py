# streamlit run src/testbench_streamlit.py

import streamlit as st
import time

@st.dialog("LLM Tool Confirmation")
def confirmation(action):
    st.write(f"Allow the LLM to run this action?\n\n{action}")

    left, right = st.columns(2)
    if left.button("Submit", use_container_width=True):
        print("submit click")
        st.session_state.confirmation_choice = True
        st.session_state.confirmation_pause = False
        st.rerun()
    elif right.button("Cancel", use_container_width=True):
        st.session_state.confirmation_choice = False
        st.session_state.confirmation_pause = False
        st.rerun()

def pause_for_confirmation(action):
    confirmation(action)
    st.session_state.confirmation_pause = True
    st.session_state.confirmation_choice = False
    
    while st.session_state.confirmation_pause:
        time.sleep(0.2)
        st.rerun()

    return st.session_state.confirmation_choice

def calculator_adder(num1: float, num2: float) -> float:
    '''Return the sum of 2 numbers'''
    if not pause_for_confirmation(f"Add numbers {num1} and {num2}"):
        return "Tool call failed. User declined permissions."
    
    return num1 + num2

left, middle, right = st.columns(3)
if left.button("Plain button", use_container_width=True):
    left.markdown(f"You clicked the plain button. {calculator_adder(1, 5)}")
    
if middle.button("Emoji button", icon="😃", use_container_width=True):
    middle.markdown("You clicked the emoji button.")
if right.button("Material button", icon=":material/mood:", use_container_width=True):
    right.markdown("You clicked the Material button.")

time.sleep(1)
while True:
    time.sleep(1)
    print("adder status:", calculator_adder(1,5))
    if True:
        break