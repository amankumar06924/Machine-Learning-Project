import streamlit as st
from myproject import workflow
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title='AI Chat', page_icon='💬')

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

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

    # try:
    #     response = workflow.invoke(
    #         {'messages': conversation},
    #         config={'configurable': {'thread_id': 'thread_12345'}},
    #     )

    #     ai_response = None
    #     if isinstance(response, dict):
    #         messages = response.get('messages', [])
    #         if messages:
    #             ai_response = getattr(messages[-1], 'content', None)

    #     if not ai_response:
    #         ai_response = 'Sorry, I could not get a response from the AI.'
    # except Exception as exc:
    #     ai_response = f'Error: {exc}'


    with st.chat_message('assistant'):
       ai_response = st.write_stream(
            message_chunk.content for message_chunk,metadata in  workflow.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config={'configurable': {'thread_id': 'thread_12345'}},
                stream_mode='messages'
            )
        )
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_response})









    