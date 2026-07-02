# Minnarino Twitch Bot 🤖

An autonomous, AI-powered Twitch chatbot written in Python using `twitchio` and the Groq API (Llama 3.3).

**Inspiration & Credits:** 
This project is heavily inspired by the Italian content creator **[Enkk](https://www.youtube.com/@enkk)** and his experiment with an AI agent named *["Minnarone"](https://www.youtube.com/watch?v=EkunaRO0uKg)*. The name *"Minnarino"* is a direct homage to his work. My goal as a computer science student was to study his architecture and recreate the core concepts of his autonomous bot on a smaller, educational scale.

## Features
- **Contextual Awareness:** Remembers the last 10 chat messages using a circular queue (`collections.deque`) to maintain the context of the conversation.
- **Autonomous Interactions:** Periodically monitors human activity and intervenes spontaneously if the chat is active, avoiding the "AI echo chamber" effect.
- **Humanized Typing:** Simulates human reading and typing delays based on the length of the generated response.
- **Asynchronous Architecture:** Built on Python's `asyncio` to prevent blocking the event loop during API calls and chat monitoring.

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/chamered/minnarino-twitch-bot.git
   cd minnarino-twitch-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate # On Mac/Linux
   ```

3. Install dependencies:
   ```bash
   pip install twitchio groq python-dotenv
   ```

4. Create a `.env` file in the root directory and add your keys:
   ```env
   TWITCH_TOKEN=oauth:your_twitch_token
   GROQ_API_KEY=your_groq_api_key
   ```

5. Create a `soul.txt` file in the root directory and write the bot's system prompt (its personality).

6. Run the bot:
   ```bash
   python3 bot.py
   ```