"""
Basic Gemini API test script

Prerequisites:
    pip install google-generativeai
    export GEMINI_API_KEY="your_api_key_here"

Run:
    python test_gemini.py
"""

import os
import google.generativeai as genai


# Save API key in variable api_key
api_key = ""

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key = api_key)


# Select Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")


# Send a test prompt
prompt = "Explain quantum computing in simple terms."

try:
    response = model.generate_content(prompt)
    print(response.text)

except Exception as e:
    print("Error calling Gemini API:")
    print(e)
