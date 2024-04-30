import streamlit as st
import pathlib
import textwrap
import os
import google.generativeai as genai
import requests


# name="generate-num-5356"
# model_name="models/gemini-1.0-pro"


context='''
Imagine you are a chatbot and buddy for elderly can you communicate with me with empathy, don't give me suggestions, just listen and show understanding. Now respond to the following prompt\n'''


def get_response(prompt):
    base_url="https://generativelanguage.googleapis.com"
    headers={
      'Authorization': 'Bearer ' + os.environ['access_token'],
      'Content-Type': 'application/json',
      'x-goog-user-project': os.environ['project_id']
    }
    name="tunedModels/generate-num-5356"
    m = requests.post(
        url = f'{base_url}/v1beta/{name}:generateContent',
        headers=headers,
        json= {
             "contents": [{
                 "parts": [{
                     "text": prompt
                 }]
              }]
        })
    
    import pprint
    print("result is",m.json())
    pprint.pprint(m.json())
    
    
    print(m.json()["candidates"][0]["content"]["parts"][0]["text"])    
    return m.json()["candidates"][0]["content"]["parts"][0]["text"]



st.title("Assistant Bot")
st.header("Share your life with me")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    meta_prompt=context+prompt
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    answer= get_response(meta_prompt)    
    response = f"Echo: {answer}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})