import os
from groq import AsyncGroq

class MinnarinoBrain:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

        with open("soul.txt", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()
    
    async def think_response(self, chat_history):
        chat_context = "\n".join(chat_history)
        instructions = f"Ecco la chat:\n{chat_context}\n\nRispondi in modo naturale e coerente all'ultimo messaggio come se fossi Minnarino."

        return await self._call_api(instructions)
    
    async def think_spontaneously(self, chat_history):
        chat_context = "\n".join(chat_history)
        instructions = f"Ecco la chat:\n{chat_context}\n\nFai un'osservazione spontanea o una battuta su quello di cui stanno parlando. Non rispondere a una persona in particolare, comportati come uno che si intromette nel discorso."

        return await self._call_api(instructions)
    
    async def _call_api(self, user_instruction: str) -> str:
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_instruction}
            ],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content