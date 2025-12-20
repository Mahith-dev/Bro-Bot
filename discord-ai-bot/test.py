import os
from dotenv import load_dotenv
from google import genai  # correct import for the new SDK

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create the client with your API key
client = genai.Client(api_key=GEMINI_API_KEY)

# Create a chat session
chat = client.chats.create(model="gemini-2.5-flash")

# Send a single message
response = chat.send_message("Say hi in a sassy way")

print("Gemini response:", response.text)
