import os
import asyncio
from dotenv import load_dotenv
from collections import deque
from twitchio.ext import commands
from rich.markup import escape

from core.ai_brain import MinnarinoBrain
from core.utils import simulated_typing_delay

load_dotenv()

class Bot(commands.Bot):
    def __init__(self, gui_log_callback=None):
        super().__init__(
            token=os.getenv("TWITCH_TOKEN"),
            prefix='!',
            initial_channels=['minnarinoo']
        )
        self.brain = MinnarinoBrain()
        self.aliases = ["minnarino", "minnarinoo", "minna", "rino"]
        self.chat_history = deque(maxlen=10)
        self.human_messages = 0
        self.gui_log = gui_log_callback
    
    def log(self, message: str):
        if self.gui_log:
            self.gui_log(message)
        else:
            print(message)
    
    async def event_ready(self):
        self.log(f'[SYSTEM] Logged in as: {self.nick}')
        if not getattr(self, 'background_timer_started', False):
            asyncio.create_task(self.spontaneous_loop())
            self.background_timer_started = True
    
    async def event_message(self, message):
        if message.author is None or message.author.name.lower() == self.nick.lower():
            return
        
        safe_text = escape(message.content)
        self.log(f'[cyan]<{message.author.name}>[/cyan] {safe_text}')

        chat_row = f'{message.author.name}: {message.content}'
        self.chat_history.append(chat_row)

        self.human_messages += 1

        msg_lower = message.content.lower()

        if any(alias in msg_lower for alias in self.aliases):
            self.log('[AI] Thinking and writing response (Tagged)...')

            ai_response = await self.brain.think_response(self.chat_history)
            await simulated_typing_delay(ai_response, read_time=5.0)

            await message.channel.send(ai_response)
            self.log(f'> {ai_response}')

            self.chat_history.append(f'{self.nick}: {ai_response}')

            self.human_messages = 0
        
        await self.handle_commands(message)

    async def spontaneous_loop(self):
        while True:
            await asyncio.sleep(60)

            try:
                if self.human_messages < 3:
                    self.log('[BACKGROUND] Chat history too short for spontaneous response. Skipping.')
                    continue

                self.log('[BACKGROUND] Timer triggered. Checking for spontaneous response opportunity...')

                if not self.connected_channels:
                    self.log('[SYSTEM] Error: No connected channels.')
                    return
                
                twitch_channel = self.connected_channels[0]

                ai_response = await self.brain.think_spontaneously(self.chat_history)
                await simulated_typing_delay(ai_response, read_time=0.0)

                await twitch_channel.send(ai_response)
                self.log(f'> {ai_response}')

                self.chat_history.append(f'{self.nick}: {ai_response}')
                self.human_messages = 0
            except Exception as e:
                self.log(f'[SYSTEM] Critical timer error: {e}')