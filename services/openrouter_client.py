import aiohttp
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for OpenRouter API to access various LLM models."""
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-bot-domain.com",  # Replace with your domain
            "X-Title": "SharahBot"
        }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Optional[str]:
        """
        Send a chat completion request to OpenRouter.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=60
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.exception(f"Error calling OpenRouter: {e}")
            return None
    
    async def get_available_models(self) -> List[Dict]:
        """
        Fetch list of available models from OpenRouter.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/models",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                return []