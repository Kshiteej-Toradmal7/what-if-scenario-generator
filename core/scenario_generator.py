
import streamlit as st
from groq import Groq

from core.prompt_builder import build_prompt


@st.cache_resource
def get_groq_client():

    api_key = st.secrets["GROQ_API_KEY"]

    return Groq(api_key=api_key)


def generate_scenario(scenario, perspectives, detail):

    try:

        client = get_groq_client()

        system_prompt, user_prompt = build_prompt(
            scenario,
            perspectives,
            detail
        )

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],

            temperature=0.8,
            max_tokens=1800
        )

        return response.choices[0].message.content

    except Exception as error:

        raise error
