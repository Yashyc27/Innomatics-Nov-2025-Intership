import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class FinanceBotEngine:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API Key missing! Check your .env file.")
        
        # New 2026 SDK Client initialization
        self.client = genai.Client(api_key=api_key)
        
        # Using the current stable flagship model
        self.model_id = 'gemini-2.5-flash'
        
        # Advanced Prompt Engineering
        self.system_prompt = """
        ROLE: You are 'Penny Wise', a witty and brilliant Indian Financial Consultant.
        
        GOAL: Help users navigate Indian banking (SBI, UPI, YONO), SIPs, Mutual Funds, and Tax regimes.
        
        TONE: Professional, empathetic, and punny. Use finance puns sparingly (e.g., "Making cents of your money").
        
        INSTRUCTIONS:
        1. Always start a new session with a professional disclaimer about being an AI.
        2. Use LaTeX for math ($Interest = P \times r \times t$).
        3. Use Markdown tables for investment comparisons.
        4. If the user mentions AWS India billing, explain common RuPay/UPI rejection issues.
        """

    def start_new_session(self):
        """
        Implementation of Multi-turn conversation memory.
        Creates a stateful chat session.
        """
        return self.client.chats.create(
            model=self.model_id, 
            config={'system_instruction': self.system_prompt}
        )