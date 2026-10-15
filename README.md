# Minnarino Twitch Bot 🤖

An autonomous, AI-powered Twitch chatbot written in Python using `twitchio`, the Groq API (`openai/gpt-oss-120b`) and a `textual` TUI dashboard.

**Inspiration & Credits:** 
This project is heavily inspired by the Italian content creator **[Enkk](https://www.youtube.com/@enkk)** and his experiment with an AI agent named *["Minnarone"](https://www.youtube.com/watch?v=EkunaRO0uKg)*. The name *"Minnarino"* is a direct homage to his work. My goal as a computer science student was to study his architecture and recreate the core concepts of his autonomous bot on a smaller, educational scale.

## Features
- **Contextual Awareness:** Remembers the last 10 chat lines using a circular queue (`collections.deque`) to maintain the context of the conversation.
- **Tag-Based Replies:** Answers whenever a message contains one of its aliases (`minnarino`, `minnarinoo`, `minna`, `rino`) as a whole word (word-boundary match, so words such as "carino" don't trigger it).
- **Intent Radar:** After replying to a user, the bot keeps that user on a 60-second "radar". New messages from them (when not tagged) are sent to a dedicated YES/NO intent check that decides whether they are really addressed to the bot.
- **Autonomous Interactions:** A background loop runs every time 60 seconds have passed since the bot's last message and posts a spontaneous observation when at least 3 new human messages have arrived since then, avoiding the "AI echo chamber" effect.
- **Director Mode:** Text typed in the dashboard that is not a `/fact` or `/clear` command is treated as a direct instruction to the bot ("director action"): the bot generates and posts a message that follows it while staying in character.
- **Live Facts Memory:** Facts added with `/fact <text>` (e.g. "we are playing Minecraft") are persisted to `data/facts.json` and injected into every prompt as live context of the stream. `/clear` erases them all.
- **Humanized Typing:** Simulates a human-like delay before answering: a reading pause plus a typing time proportional to the response length (spontaneous and directed messages skip the reading pause).
- **Safe Replies:** Empty or failed AI responses are detected and skipped instead of being posted to chat.
- **TUI Dashboard:** A `textual` control center showing chat, bot replies and system logs side by side, with an input to manage facts and direct the bot.
- **Asynchronous Architecture:** Built on Python's `asyncio` to prevent blocking the event loop during API calls and chat monitoring.
- **TUI Dashboard:** A `textual` control center showing chat, bot replies and system logs side by side, with an input to manage the bot's facts.
- **Asynchronous Architecture:** Built on Python's `asyncio` to prevent blocking the event loop during API calls and chat monitoring.

## Project Structure
```text
dashboard.py        # Entry point: TUI dashboard, boots the bot
core/
  bot.py            # Twitch connection, reply logic, radar, spontaneous loop
  ai_brain.py       # Groq API: persona, replies, intent check, facts persistence
  utils.py          # Simulated typing delay
data/
  soul.txt          # System prompt (bot personality)
  facts.json        # Persisted live facts
.env                # TWITCH_TOKEN and GROQ_API_KEY (not committed)
```

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

3. Install all the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your keys:
   ```env
   TWITCH_TOKEN=oauth:your_twitch_token
   GROQ_API_KEY=your_groq_api_key
   ```

5. Edit `data/soul.txt` to customize the bot's system prompt (its personality).

6. Run the dashboard from the project root:
   ```bash
   python3 dashboard.py
   ```

   The bot joins the channel `minnarinoo` by default — change `initial_channels` in `core/bot.py` to join another one.

## Using the Dashboard

- **CHAT** panel (left): live Twitch chat.
- **MINNARINO** panel (right, top): the messages sent by the bot.
- **SYSTEM** panel (right, bottom): system, radar and background-loop logs.
- **Input** (bottom):
  - `/fact <text>` adds a fact to the bot's live context (persisted to `data/facts.json`).
  - `/clear` erases all stored facts.
  - Any other text is a **director action**: the bot posts a message following that instruction while staying in character.
- Press `q` to quit.
