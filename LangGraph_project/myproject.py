import os
import operator
from typing import TypedDict, Annotated, Literal, Type
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import google.genai as genai
from google.genai import types
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("Please set GOOGLE_API_KEY in your environment or .env file.")
client = genai.Client(api_key=api_key)
MODEL_ID = 'gemini-2.5-flash'

class EvaluationSchema(BaseModel):
    messages: str = Field(description='you are smart ai')

def get_structured_evaluation(prompt: str) -> EvaluationSchema:
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EvaluationSchema,
        ),
    )
    return EvaluationSchema.model_validate_json(response.text)

from langgraph.graph.message import add_messages
class chatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def chat_node(state:chatState):
    messages = state['messages']
    if isinstance(messages, list):
        prompt = "\n".join(m.content for m in messages if hasattr(m, 'content'))
    else:
        prompt = str(messages)
    eval_result = get_structured_evaluation(prompt)
    from langchain_core.messages import AIMessage
    return {'messages':[AIMessage(content=eval_result.messages)]}


checkpoint = MemorySaver()
graph = StateGraph(chatState)
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)
workflow = graph.compile(checkpointer=checkpoint)
















# workflow

# thread_id = "thread_12345"
# initial_state = {'messages': []}

# while True:
#     user_input = input("hey nice to meet you what you want today: ")
#     if user_input.lower() in ['exit', 'quit', 'bye']:
#         print("Exiting the chat.")
#         break

#     config = {"configurable": {"thread_id": thread_id}}
#     initial_state['messages'].append(HumanMessage(content=user_input))
#     result = workflow.invoke(initial_state, config=config)
#     initial_state = result

#     ai_messages = [m for m in result.get('messages', []) if isinstance(m, AIMessage)]
#     ai_only = ai_messages[-1].content if ai_messages else None
#     print(f"AI: {ai_only}")
