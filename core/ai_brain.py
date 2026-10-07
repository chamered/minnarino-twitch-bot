import os
import json
from groq import AsyncGroq

class MinnarinoBrain:
    """AI persona: builds prompts from live facts and chat history, then calls Groq for replies and intent checks."""
    def __init__(self):
        """Create the Groq client, load the persona prompt from data/soul.txt and the persisted facts."""
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

        with open("data/soul.txt", "r", encoding="utf-8") as file:
            self.system_prompt = file.read()
        
        self.facts_file = "data/facts.json"
        self.facts = self.load_facts()
    
    def load_facts(self) -> list:
        """Load facts from the JSON file, returning an empty list if it is missing or invalid."""
        if os.path.exists(self.facts_file):
            with open(self.facts_file, "r", encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        else:
            return []
    
    def save_facts(self):
        """Persist the current facts list to the JSON file."""
        with open(self.facts_file, "w", encoding="utf-8") as file:
            json.dump(self.facts, file, indent=4)
    
    def add_fact(self, fact: str):
        """Append a fact to memory and persist it."""
        self.facts.append(fact)
        self.save_facts()
    
    def clear_facts(self):
        """Forget every stored fact and persist the change."""
        self.facts = []
        self.save_facts()

    def _build_context(self, chat_history: list) -> str:
        """Assemble the prompt context from the live facts and the recent chat history."""
        context = ""

        if self.facts:
            context += "[CONTESTO ATTUALE DELLA LIVE - tienine conto per capire la situazione]:\n"
            for fact in self.facts:
                context += f"- {fact}\n"
            context += "\n"
        
        context += "[CHAT RECENTE]:\n" + "\n".join(chat_history)
        return context
    
    async def think_response(self, chat_history):
        """Generate a natural in-character reply to the latest chat message."""
        full_context = self._build_context(chat_history)
        instructions = f"{full_context}\n\nRispondi in modo naturale e coerente all'ultimo messaggio come se fossi Minnarino."
        return await self._call_api(instructions)
    
    async def think_spontaneously(self, chat_history):
        """Generate an unprompted observation that jumps into the ongoing conversation."""
        full_context = self._build_context(chat_history)
        instructions = f"{full_context}\n\nFai un'osservazione spontanea o una battuta. Non rispondere a una persona in particolare, comportati come uno che si intromette nel discorso."
        return await self._call_api(instructions)
    
    async def _call_api(self, user_instruction: str) -> str:
        """Send the system prompt plus the instructions to Groq and return the answer text."""
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_instruction}
            ],
            model="openai/gpt-oss-120b",
        )
        return response.choices[0].message.content

    async def check_intent(self, chat_history, author: str, message_content: str) -> bool:
        """Ask the model for a plain YES/NO verdict on whether the latest message targets the bot."""
        recent_context = "\n".join(list(chat_history)[-5:])
        
        prompt = (
            "Sei un arbitro logico. Il tuo scopo è analizzare la chat e rispondere SOLO con 'YES' o 'NO'.\n"
            f"Contesto della chat:\n{recent_context}\n\n"
            f"L'utente '{author}' ha appena scritto: '{message_content}'.\n"
            "Domanda: Considerando che il bot si chiama 'minnarino' e stava conversando recentemente con questo utente, questo nuovo messaggio è chiaramente rivolto a minnarino o è la continuazione del loro discorso?\n"
            "Rispondi SOLO YES o NO senza alcuna punteggiatura o testo aggiuntivo."
        )
        
        try:
            response = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="openai/gpt-oss-120b",
                max_tokens=5,
                temperature=0.0
            )
            answer = response.choices[0].message.content.strip().upper()
            return "YES" in answer
        except Exception:
            # On API errors assume the message is not for us, to avoid unwanted replies
            return False