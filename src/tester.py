from ModelGraph import MyGraph
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
    graph = MyGraph()
    graph.call("what is 8 * 10, 9^5, and 3195 + 98? What's the sum of all 3 solutions?")

test_graph_call()

