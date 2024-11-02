from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode

@tool
def calculator_adder(num1: float, num2: float) -> float:
    '''Return the sum of 2 numbers'''
    return str(num1 + num2)

@tool
def calculator_multiplier(num1: float, num2: float) -> float:
    '''Return the product of 2 numbers'''
    return str(num1 * num2)

@tool
def calculator_exponent(base: float, exponent: float) -> float:
    '''Return the exponentiation of the "base" to the power of "exponent"'''
    return str(base ** exponent)

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

tools = [calculator_adder, calculator_exponent, calculator_multiplier]
# tools = [calculator_multiplier]

def create_tool_node_with_fallback() -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )

