import os
import asyncio
from typing import Optional, List
import gpt4all
import openai
import google.generativeai as genai
from anthropic import Anthropic
import httpx
import aiohttp

class GPT4AllService:
    def __init__(self):
        model_path = os.getenv('GPT4ALL_MODEL_PATH', 'models/orca-mini-3b.ggmlv3.q4_0.bin')
        self.model = gpt4all.GPT4All(model_path)

    async def generate(self, prompt: str) -> str:
        try:
            with self.model.chat_session():
                response = self.model.generate(prompt, max_tokens=200)
                return response
        except Exception as e:
            raise Exception(f"GPT4All generation failed: {str(e)}")

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise Exception("OpenAI API key not found")
        try:
            client = openai.AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI generation failed: {str(e)}")

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise Exception("Google API key not found")
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = await model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini generation failed: {str(e)}")

class ClaudeService:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)

    async def generate(self, prompt: str) -> str:
        if not self.api_key:
            raise Exception("Anthropic API key not found")
        try:
            message = await self.client.messages.create_async(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude generation failed: {str(e)}")

class HybridAIClient:
    def __init__(self):
        self.services = [
            GPT4AllService(),
            OpenAIService(),
            GeminiService(),
            ClaudeService()
        ]

    async def generate_response(self, prompt: str) -> str:
        for service in self.services:
            try:
                response = await service.generate(prompt)
                if response and len(response.strip()) > 0:
                    return response
            except Exception as e:
                print(f"Service {type(service).__name__} failed: {str(e)}")
                continue
        raise Exception("All AI services failed")