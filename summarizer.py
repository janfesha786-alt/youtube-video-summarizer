import streamlit as st
from google import genai


GEMINI_API_KEY=st.secrets["GEMINI_API_KEY"]


client = genai.Client(api_key=GEMINI_API_KEY)

def summarize(transcript,summary_length,summary_format):

    prompt = f"""Summarize the following YouTube transcript.

    summary length: {summary_length}
    summary format: {summary_format}

    Instructions:
    
    If the format is paragraph:
    write the summary as clear, connected paragraphs.

    If the format is Bullet points:
    Present the key information as concise bullet points.

    If the format is study notes:
    create structured study notes with headings,
    important concepts, and key points.

    If the length is short, keep the summary around 200 words.
    If the length is Medium, keep it around 300 words.
    If the length is detailed, provide around 500 words.

    Focus on the key ideas and important information.

    Transcript:
    {transcript}
    """


    response = client.models.generate_content(
        model = "gemini-3.6-flash",
        contents = prompt)

    return response.text
