import os
from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    @abstractmethod
    def ask(self, prompt: str, json_mode: bool = False) -> str:
        pass

    @abstractmethod
    async def ask_async(self, prompt: str, json_mode: bool = False) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        from openai import OpenAI, AsyncOpenAI
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.model = model

    def ask(self, prompt: str, json_mode: bool = False) -> str:
        response_format = {"type": "json_object"} if json_mode else None
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format
        )
        return response.choices[0].message.content

    async def ask_async(self, prompt: str, json_mode: bool = False) -> str:
        response_format = {"type": "json_object"} if json_mode else None
        response = await self.async_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_format
        )
        return response.choices[0].message.content

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20240620"):
        from anthropic import Anthropic, AsyncAnthropic
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)
        self.model = model

    def ask(self, prompt: str, json_mode: bool = False) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    async def ask_async(self, prompt: str, json_mode: bool = False) -> str:
        message = await self.async_client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        import google.generativeai as genai
        genai.configure(api_key=api_key or os.environ.get("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model)

    def ask(self, prompt: str, json_mode: bool = False) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    async def ask_async(self, prompt: str, json_mode: bool = False) -> str:
        response = await self.model.generate_content_async(prompt)
        return response.text

class MockProvider(LLMProvider):
    def __init__(self, **kwargs):
        pass

    def ask(self, prompt: str, json_mode: bool = False) -> str:
        if json_mode:
            return '{"library": "Unknown", "confidence_score": 0.0, "reasoning": "Mock identification"}'
        return "This is a mock response identifying the library as 'Unknown'."

    async def ask_async(self, prompt: str, json_mode: bool = False) -> str:
        import asyncio
        await asyncio.sleep(0.1)
        if json_mode:
            return '{"library": "Unknown", "confidence_score": 0.0, "reasoning": "Mock identification"}'
        return "This is a mock response identifying the library as 'Unknown'."

def get_provider(name: str, **kwargs) -> LLMProvider:
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "mock": MockProvider
    }
    if name not in providers:
        raise ValueError(f"Unknown provider: {name}")
    return providers[name](**kwargs)
