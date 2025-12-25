import discord
import os
import random
import asyncio
import time
import requests
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# ------------------- LOAD ENV -------------------
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ------------------- FLASK (KEEP ALIVE) -------------------
app = Flask("")

@app.route("/")
def home():
    return "Bro bot online."

def run():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run).start()

# ------------------- DISCORD SETUP -------------------
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

BOT_NAMES = ["ai bot", "bro bot", "aibot", "brobot"]
COOLDOWN_SECONDS = 5
last_response_time = 0

# ------------------- GEMINI FUNCTION -------------------
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models:generateText"

PERSONALITY_PROMPT = """
You are a real person in a Discord friend group.
Vibe:
- Chill gamer, confident, casual, not cringe
- Can roast friends lightly
- Knows the group well, like longtime friends
- Speaks casually, naturally, sometimes sarcastic, sometimes serious
- Can give detailed answers if needed
- Reacts like a human; can say “idk”, “depends”, or pause sometimes
- NEVER say you are an AI or mention policies
- Your goal: hang out, chat, joke, answer questions naturally
"""

def send_to_gemini(prompt):
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gemini-1.5-flash",  # change if newer models available
        "input": f"{PERSONALITY_PROMPT}\n\n{prompt}",
        "temperature": 0.9,
        "maxOutputTokens": 300
    }

    try:
        response = requests.post(GEMINI_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        # Gemini's text output is nested, check the returned keys
        text = result.get("candidates", [{}])[0].get("content", "")
        return text.strip() if text else "bruh idk"
    except Exception as e:
        print("Gemini HTTP error:", e)
        return "nah my brain just lagged 💀"

# ------------------- DISCORD EVENTS -------------------
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    global last_response_time
    if message.author.bot:
        return

    content = message.content.lower()
    print(f"Message from {message.author}: {message.content}")

    # Decide if bot should respond
    mentioned = client.user and client.user in message.mentions
    name_called = any(name in content for name in BOT_NAMES)
    random_chime = random.random() < 0.03  # 3% chance to randomly chime

    if not (mentioned or name_called or random_chime):
        return

    # Rate limit
    current_time = time.time()
    if current_time - last_response_time < COOLDOWN_SECONDS:
        return
    last_response_time = current_time

    # Clean prompt
    prompt = message.content
    for name in BOT_NAMES:
        prompt = prompt.replace(name, "")
    if client.user:
        prompt = prompt.replace(f"<@{client.user.id}>", "").replace(f"<@!{client.user.id}>", "").strip()
    if not prompt:
        prompt = "React naturally to the conversation."

    # Human-like typing delay
    await asyncio.sleep(random.uniform(0.6, 1.6))

    # Call Gemini REST API
    text = send_to_gemini(prompt)
    await message.channel.send(text)

# ------------------- RUN -------------------
if DISCORD_TOKEN:
    client.run(DISCORD_TOKEN)
else:
    print("Error: DISCORD_TOKEN not found in environment variables")
