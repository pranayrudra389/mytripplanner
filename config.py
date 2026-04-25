import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

load_dotenv()

@dataclass
class LLMConfig:
    provider: str
    model_name: str
    temperature: float
    base_url: str | None = None
    
def get_config_from_env() -> LLMConfig:
    provider = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    temperature_str = os.getenv("TEMPERATURE", "0.2")
    
    try:
        temperature = float(temperature_str)
    except ValueError as exc:
        raise ValueError("TEMPERATURE must be a valid number") from exc    
    
    if provider == "openai":
        model_name = os.getenv("OPENAI_MODEL")
        if not model_name:
            raise ValueError("OPENAI_MODEL is required when LLM_PROVIDER=openai")
        return LLMConfig(
            provider="openai",
            model_name=model_name,
            temperature=temperature,
        )
        
    if provider == "ollama":
        model_name = os.getenv("OLLAMA_MODEL")
        if not model_name:
            raise ValueError("OLLAMA_MODEL is required when LLM_PROVIDER=ollama")
        return LLMConfig(
            provider="ollama",
            model_name=model_name,
            temperature=temperature,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
    
    raise ValueError("LLM_PROVIDER must be either 'openai' or 'ollama'")

def get_llm_model(config: LLMConfig):
    if config.provider == "openai":
        return ChatOpenAI(
            model=config.model_name,
            temperature=config.temperature,
        )
    if config.provider == "ollama":
        return ChatOllama(
            model=config.model_name,
            temperature=config.temperature,
            base_url=config.base_url,
        )
    raise ValueError(f"Unsupported provider: {config.provider}")
