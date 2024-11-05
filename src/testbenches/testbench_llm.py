from ModelGraph import AgentGraph
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

def test_ollama():
    llm = ChatOllama(model="llama3.2")
    
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is 8 * 10?")
    ]

    print("ollama test", llm.invoke(messages))

def test_graph_call():
    graph = AgentGraph()
    # graph.call("what is 8 * 10, 9^5, and 3195 + 98? What's the sum of all 3 solutions?")
    # graph.call("Can you send an email to my professor telling him I will be late to class tomorrow?")
    # graph.call("put on my calendar to meet with my professor tomorrow at 10 AM")
    # graph.call("hello!")

test_graph_call()

