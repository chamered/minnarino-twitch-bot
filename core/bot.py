import os
import time
import asyncio
from dotenv import load_dotenv
from collections import deque
from twitchio.ext import commands
from rich.markup import escape

from core.ai_brain import MinnarinoBrain
from core.utils import simulated_typing_delay

load_dotenv()

class Bot(commands.Bot):
    """Twitch bot that replies when tagged by an alias or when the intent check confirms a message targets it."""
    def __init__(self, gui_log_callback=None):
        """Set up the AI brain, trigger aliases, rolling chat history and the radar of recent conversation partners."""
        super().__init__(
            token=os.getenv("TWITCH_TOKEN"),
            prefix='!',
            initial_channels=['minnarinoo']
        )
        self.brain = MinnarinoBrain()
        self.aliases = ["minnarino", "minnarinoo", "minna", "rino"]
        self.chat_history = deque(maxlen=10)
        self.human_messages = 0
        self.active_conversations = {}
        self.gui_log = gui_log_callback
    
    def log(self, message: str):
        """Forward a log line to the GUI callback, or print it when no callback is set."""
        if self.gui_log:
            self.gui_log(message)
        else:
            print(message)
    
    async def event_ready(self):
        """Confirm login and start the spontaneous-message loop exactly once."""
        self.log(f'[SYSTEM] Logged in as: {self.nick}')
        if not getattr(self, 'background_timer_started', False):
            asyncio.create_task(self.spontaneous_loop())
            self.background_timer_started = True
    
    async def event_message(self, message):
        """Record an incoming message, then reply if the bot was tagged or the intent check confirms it targets us."""
        if message.author is None or message.author.name.lower() == self.nick.lower():
            return
        
        author = message.author.name.lower()
        safe_text = escape(message.content)
        self.log(f'[cyan]<{message.author.name}>[/cyan] {safe_text}')

        chat_row = f'{message.author.name}: {message.content}'
        self.chat_history.append(chat_row)
        self.human_messages += 1

        msg_lower = message.content.lower()

        is_tagged = any(alias in msg_lower for alias in self.aliases)
        
        is_in_radar = False
        current_time = time.time()
        
        if not is_tagged and author in self.active_conversations:
            if current_time - self.active_conversations[author] < 60:
                self.log(f'[SYSTEM] {author} is in the radar. Checking if their message is for us...')
                
                is_in_radar = await self.brain.check_intent(self.chat_history, message.author.name, message.content)
                
                if is_in_radar:
                    self.log(f'[SYSTEM] Intent confirmed. {author} is talking to us!')
                else:
                    self.log(f'[SYSTEM] False alarm. {author} was not talking to us.')
            else:
                del self.active_conversations[author]
                self.log(f'[SYSTEM] Radar expired for {author}.')

        if is_tagged or is_in_radar:
            self.log('[SYSTEM] The AI is processing the reply...')

            ai_response = await self.brain.think_response(self.chat_history)
            await simulated_typing_delay(ai_response, read_time=5.0)

            await message.channel.send(ai_response)
            self.log(f'> {ai_response}')

            self.chat_history.append(f'{self.nick}: {ai_response}')
            self.human_messages = 0
            
            self.active_conversations[author] = time.time()
        
        await self.handle_commands(message)

    async def spontaneous_loop(self):
        """Every 60 seconds, post an AI observation if at least 3 human messages arrived since the last bot post."""
        while True:
            await asyncio.sleep(60)

            try:
                if self.human_messages < 3:
                    self.log('[BACKGROUND] Chat history too short. Skipping spontaneous reply.')
                    continue

                self.log('[BACKGROUND] Timer fired with enough activity. Generating a spontaneous message...')

                if not self.connected_channels:
                    self.log('[BACKGROUND] Error: No connected channels. Spontaneous loop stopped.')
                    return
                
                twitch_channel = self.connected_channels[0]

                ai_response = await self.brain.think_spontaneously(self.chat_history)
                await simulated_typing_delay(ai_response, read_time=0.0)

                await twitch_channel.send(ai_response)
                self.log(f'> {ai_response}')

                self.chat_history.append(f'{self.nick}: {ai_response}')
                self.human_messages = 0
            except Exception as e:
                self.log(f'[BACKGROUND] Unexpected error in spontaneous loop: {e}')