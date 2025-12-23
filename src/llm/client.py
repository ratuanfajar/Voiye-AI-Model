"""LLM client wrapper. Keep API keys in .env and prompts in config/prompt_templates.yaml"""

import os

class LLMClient:
    def __init__(self, provider: str = "openai"):
        self.provider = provider

    def call(self, prompt: str) -> str:
        # placeholder for API call
        return "response"
