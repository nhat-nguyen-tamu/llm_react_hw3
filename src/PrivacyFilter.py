from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class PrivacyFilter():
    def __init__(self, llm, user_input):
        messages = [
            SystemMessage(content="You are a middleman AI agent. Your task is to analyze incoming prompts and replace private information with placeholders. You may replace the following private information with one of these tokens: [EMAIL] [NAME] [PHONE] [ADDRESS]"),

            HumanMessage(content="Joe Radford: hello! I'm calling about the pipe leak in my apartment 156 Grove Street Apt. #43 San Andreas. Let me know when it's fixed! my callback number is 234-858-4498."),

            AIMessage(content=f"{user_input}"),
            HumanMessage(content=f"{user_input}"),
        ]

        response = llm.invoke(messages)
        self.message = response.content