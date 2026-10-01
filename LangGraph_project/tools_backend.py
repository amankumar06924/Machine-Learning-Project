import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import sqlite3

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("Please set GOOGLE_API_KEY in your environment.")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)

class chatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

search_tool = DuckDuckGoSearchRun(region="us-en")
@tool
def calculator(x: float, y: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        op = operation.strip().lower()
        if op == "add": return {"result": x + y}
        elif op == "sub": return {"result": x - y}
        elif op == "mul": return {"result": x * y}
        elif op == "div":
            if y == 0: return {"error": "division by zero"}
            return {"result": x / y}
        else: return {"error": f"unsupported operation: {operation}"}
    except Exception as e:
        return {"error": str(e)}

tools = [calculator, search_tool]

llm_with_tools = llm.bind_tools(tools)

def tool_chat_node(state: chatState):
    """LLM node that decides to answer or trigger a tool call."""
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {'messages': [response]}

tool_node = ToolNode(tools)

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpoint = SqliteSaver(conn=conn)

graph = StateGraph(chatState)
graph.add_node('agent', tool_chat_node)
graph.add_node('tools', tool_node)
graph.add_edge(START, 'agent')
graph.add_conditional_edges('agent',tools_condition,)
graph.add_edge('tools', 'agent')

workflow = graph.compile(checkpointer=checkpoint)

def retrive_all_threads():
    all_threads = set()
    try:
        for checkp in checkpoint.list(None):
            all_threads.add(checkp.config['configurable']['thread_id'])
    except Exception:
        pass
    return list(all_threads)