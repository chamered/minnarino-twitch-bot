import os
import asyncio
from dotenv import load_dotenv
from collections import deque
from twitchio.ext import commands, routines

from ai_brain import MinnarinoBrain
from utils import simulated_typing_delay

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

        # Initialize the AI brain for generating responses
        self.brain = MinnarinoBrain()
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

            ai_response = await self.brain.think_response(self.chat_history)

            await simulated_typing_delay(ai_response, read_time=5.0)

            await message.channel.send(ai_response)
            print(f'[BOT-AI]: {ai_response}')

            # Add the bot's own response to the memory
            self.chat_history.append(f'{self.nick}: {ai_response}')

            # Reset the human activity counter after the bot speaks
            self.human_messages = 0
        
        await self.handle_commands(message)

    # Background task running every 60 seconds
    @routines.routine(seconds=60)
    async def spontaneous_loop(self):
        # Skip if there hasn't been enough human activity (avoids AI echo chamber)
        if self.human_messages < 3:
            print(f'[BACKGROUND]: Chat history too short for spontaneous response. Skipping.')
            return

        print(f'[BACKGROUND]: Timer triggered. Checking for spontaneous response opportunity...')
        twitch_channel = self.connected_channels[0]

        ai_response = await self.brain.think_spontaneously(self.chat_history)

        await simulated_typing_delay(ai_response, read_time=0.0)

        await twitch_channel.send(ai_response)
        print(f'[BOT-AI]: {ai_response}')

        self.chat_history.append(f'{self.nick}: {ai_response}')
        self.human_messages = 0

if __name__ == "__main__":
    bot = Bot()
    bot.run()