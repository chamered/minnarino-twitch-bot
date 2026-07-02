import os
from dotenv import load_dotenv
import asyncio
from twitchio.ext import commands, routines
from groq import AsyncGroq
from collections import deque

# Load environment variables from .env file
load_dotenv()

# Fix for Python 3.10+ event loop compatibility with twitchio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.getenv("TWITCH_TOKEN"),
            prefix='!',
            initial_channels=['minnarinoo']
        )

        self.ai_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

        # Load the bot's personality (system prompt) from an external file
        with open("soul.txt", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

        # Keywords that trigger the bot's direct response
        self.aliases = ["minnarino", "minnarinoo", "minna", "rino"]
        
        # Short-term memory storing the last 10 chat messages
        self.chat_history = deque(maxlen=10)

        # Counter to track human chat activity and prevent the bot from talking to itself
        self.human_messages = 0
    
    async def event_ready(self):
        print(f'Logged in as: {self.nick}')
        # Start the background task once the bot is fully connected
        self.spontaneous_loop.start()
    
    async def event_message(self, message):
        # Ignore messages without an author or sent by the bot itself
        if message.author is None or message.author.name.lower() == self.nick.lower():
            return
        
        print(f'[{message.author.name}]: {message.content}')

        # Save the new message to short-term memory
        chat_row = f'{message.author.name}: {message.content}'
        self.chat_history.append(chat_row)

        # Increment human activity counter
        self.human_messages += 1

        msg_lower = message.content.lower()

        # If the bot is mentioned, generate and send a response
        if any(alias in msg_lower for alias in self.aliases):
            print(f'[BOT-AI]: Thinking and writing response...')

            ai_response = await self.think_response()

            # Simulate human reading and typing delay
            read_time = 5.0
            write_time = len(ai_response) * 0.05
            total_delay = read_time + write_time
            await asyncio.sleep(total_delay)

            await message.channel.send(ai_response)
            print(f'[BOT-AI]: {ai_response}')

            # Add the bot's own response to the memory
            self.chat_history.append(f'{self.nick}: {ai_response}')

            # Reset the human activity counter after the bot speaks
            self.human_messages = 0
        
        await self.handle_commands(message)
    
    async def think_response(self):
        # Format the memory into a single text block
        chat_context = "\n".join(self.chat_history)

        final_instructions = f"Ecco gli ultimi messaggi della chat di Twitch:\n{chat_context}\n\nRispondi in modo naturale e coerente all'ultimo messaggio come se fossi Minnarino."

        # Make an asynchronous call to the Groq API
        chat_completion = await self.ai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": final_instructions}
            ],
            model="llama-3.3-70b-versatile",
        )

        return chat_completion.choices[0].message.content

    # Background task running every 60 seconds
    @routines.routine(seconds=60)
    async def spontaneous_loop(self):
        print(f'[BACKGROUND]: Timer triggered. Checking for spontaneous response opportunity...')

        # Skip if there hasn't been enough human activity (avoids AI echo chamber)
        if self.human_messages < 3:
            print(f'[BACKGROUND]: Chat history too short for spontaneous response. Skipping.')
            return

        twitch_channel = self.connected_channels[0]

        ai_response = await self.think_spontaneously()

        # Simulate typing delay (no reading time needed here)
        write_time = len(ai_response) * 0.05
        await asyncio.sleep(write_time)

        await twitch_channel.send(ai_response)
        print(f'[BOT-AI]: {ai_response}')

        self.chat_history.append(f'{self.nick}: {ai_response}')
        self.human_messages = 0
    
    async def think_spontaneously(self):
        chat_context = "\n".join(self.chat_history)

        final_instructions = f"Ecco la chat:\n{chat_context}\n\nFai un'osservazione spontanea o una battuta su quello di cui stanno parlando. Non rispondere a una persona in particolare, comportati come uno che si intromette nel discorso."

        chat_completion = await self.ai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": final_instructions}
            ],
            model="llama-3.3-70b-versatile",
        )

        return chat_completion.choices[0].message.content


bot = Bot()
bot.run()