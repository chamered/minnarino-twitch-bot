import os
import json
from groq import AsyncGroq

class MinnarinoBrain:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

        with open("data/soul.txt", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()
        
        self.facts_file = "data/facts.json"
        self.facts = self.load_facts()
    
    def load_facts(self) -> list:
        if os.path.exists(self.facts_file):
            with open(self.facts_file, "r", encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        else:
            return []
    
    def save_facts(self):
        with open(self.facts_file, "w", encoding="utf-8") as file:
            json.dump(self.facts, file, indent=4)
    
    def add_fact(self, fact: str):
        self.facts.append(fact)
        self.save_facts()
    
    def clear_facts(self):
        self.facts = []
        self.save_facts()

    def _build_context(self, chat_history: list) -> str:
        context = ""

        if self.facts:
            context += "[CONTESTO ATTUALE DELLA LIVE - tienine conto per capire la situazione]:\n"
            for fact in self.facts:
                context += f"- {fact}\n"
            context += "\n"
        
        context += "[CHAT RECENTE]:\n" + "\n".join(chat_history)
        return context
    
    async def think_response(self, chat_history):
        full_context = self._build_context(chat_history)
        instructions = f"{full_context}\n\nRispondi in modo naturale e coerente all'ultimo messaggio come se fossi Minnarino."
        return await self._call_api(instructions)
    
    async def think_spontaneously(self, chat_history):
        full_context = self._build_context(chat_history)
        instructions = f"{full_context}\n\nFai un'osservazione spontanea o una battuta. Non rispondere a una persona in particolare, comportati come uno che si intromette nel discorso."
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