import asyncio
import os
from typing import Dict, Any, Optional
from groq import Groq
from dataclasses import dataclass

@dataclass
class ModelResponse:
    content: str
    model: str
    usage_tokens: int
    finish_reason: str
    response_time: float

class GroqClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        # Initialize Groq client with explicit API key
        self.client = Groq(api_key=self.api_key)
    
    async def generate_response(
        self,
        prompt: str,
        model_id: str,
        max_tokens: int = 4096,
        temperature: float = 0.1,
        timeout: int = 30
    ) -> ModelResponse:
        """Generate response from Groq model"""
        import time
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=max_tokens,
                temperature=temperature,
                top_p=1,
                stream=False,
                stop=None
            )
            
            response_time = time.time() - start_time
            
            return ModelResponse(
                content=response.choices[0].message.content,
                model=model_id,
                usage_tokens=response.usage.total_tokens if response.usage else 0,
                finish_reason=response.choices[0].finish_reason,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ModelResponse(
                content=f"Error: {str(e)}",
                model=model_id,
                usage_tokens=0,
                finish_reason="error",
                response_time=response_time
            )
    
    async def test_connection(self, model_id: str) -> bool:
        """Test if the connection and model are working"""
        try:
            test_prompt = "Hello, this is a test message. Please respond with 'OK'."
            response = await self.generate_response(test_prompt, model_id, max_tokens=10)
            return response.finish_reason != "error"
        except:
            return False
    
    def get_available_models(self) -> Dict[str, str]:
        """Return mapping of available Groq models"""
        return {
            "openai/gpt-oss-20b": "GPT OSS 20B",
        }