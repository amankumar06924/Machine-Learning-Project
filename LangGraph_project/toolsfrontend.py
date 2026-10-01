import streamlit as st
from tools_backend import workflow, retrive_all_threads
from langchain_core.messages import HumanMessage, AIMessage
import uuid

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrive_all_threads()

def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
    st.session_state['message_history'] = []

def thread_message_list(thread_id):
    state = workflow.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

st.set_page_config(page_title='AI Chat', page_icon='💬')

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    reset_chat()

st.sidebar.title("Chat Control")
if st.sidebar.button('+ New Chat'):
    reset_chat()
    st.rerun()

st.sidebar.header('History')
for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(f"{str(thread_id)[:8]}...", key=f"btn_{thread_id}"):
        st.session_state['thread_id'] = thread_id
        messages = thread_message_list(thread_id)
        
        temp_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                temp_messages.append({'role': 'user', 'content': message.content})
            elif isinstance(message, AIMessage) and message.content:
                temp_messages.append({'role': 'assistant', 'content': message.content})
        st.session_state['message_history'] = temp_messages
        st.rerun()

st.title('AI Chat with Tools 🛠️')
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.write(message['content'])

user_input = st.chat_input('Ask a question or request calculations...')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.write(user_input)

    with st.chat_message('assistant'):
        with st.spinner("Processing..."):
            config = {'configurable': {'thread_id': st.session_state['thread_id']}}
            final_state = workflow.invoke(
                {'messages': [HumanMessage(content=user_input)]}, 
                config=config
            )
            final_messages = final_state.get('messages', [])
            ai_response_text = ""
            for msg in reversed(final_messages):
                if isinstance(msg, AIMessage) and msg.content:
                    ai_response_text = msg.content
                    break
            st.write(ai_response_text)
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_response_text})