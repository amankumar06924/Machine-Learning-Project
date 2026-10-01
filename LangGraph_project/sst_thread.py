import streamlit as st
from myproject import workflow
from langchain_core.messages import HumanMessage, AIMessage
import uuid

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def thread_message_list(thread_id):
    return workflow.get_state(config={'configurable': {'thread_id':thread_id}}).values['messages']



st.set_page_config(page_title='AI Chat', page_icon='💬')

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])


# add side bar 
st.sidebar.title("side bar")

if st.sidebar.button('new chat'):
    reset_chat()



st.sidebar.header('My conversations')
for thread_id in st.session_state['chat_threads'][::-1]:
 if st.sidebar.button(str(thread_id)):
    st.session_state['thread_id'] = thread_id
    messages =  thread_message_list(thread_id)

    temp_messages = []
    for message in messages:
        if isinstance(message,HumanMessage):
            role = 'user'
        else:
            role = 'assistant'
        temp_messages.append({'role':role,'content':message.content})
    st.session_state['message_history'] = temp_messages
    

########################

st.title('AI Chat')
st.write('Ask a question and get a response from the AI.')

for message in st.session_state['message_history']:
    if message['role'] == 'user':
        with st.chat_message('user'):
            st.write(message['content'])
    else:
        with st.chat_message('assistant'):
            st.write(message['content'])

user_input = st.chat_input('Type your message here...')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    conversation = []
    for message in st.session_state['message_history']:
        if message['role'] == 'user':
            conversation.append(HumanMessage(content=message['content']))
        else:
            conversation.append(AIMessage(content=message['content']))

    with st.chat_message('assistant'):
       ai_response = st.write_stream(
            message_chunk.content for message_chunk,metadata in  workflow.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config={'configurable': {'thread_id': st.session_state['thread_id']}},
                stream_mode='messages'
            )
        )
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_response})









    