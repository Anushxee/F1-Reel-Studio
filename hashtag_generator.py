import openai
import streamlit as st

openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_hashtags(transcript):
    prompt = f"Generate 10 trending and funny Instagram hashtags for the following Formula 1 clip description:\n\n{transcript}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message['content']
