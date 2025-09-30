import os
import json
import asyncio
from typing import List, Dict, Optional
from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from pydantic import BaseSettings

def keyvault_name_as_attr(name: str) -> str:
    return name.replace("-", "_").upper()

class Settings(BaseSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Try to load from Key Vault first if endpoint is available, but fall back to env vars
        if self.AZURE_KEY_VAULT_ENDPOINT and not os.getenv('CI'):
            try:
                credential = DefaultAzureCredential()
                keyvault_client = SecretClient(self.AZURE_KEY_VAULT_ENDPOINT, credential)
                secrets_loaded = 0
                for secret in keyvault_client.list_properties_of_secrets():
                    if secret.name:
                        value = keyvault_client.get_secret(secret.name).value
                        if value:  # Only set if value is not empty
                            setattr(self, keyvault_name_as_attr(secret.name), value)
                            secrets_loaded += 1
                if secrets_loaded > 0:
                    print(f"Successfully loaded {secrets_loaded} secrets from Key Vault")
                else:
                    print("Key Vault accessible but no secrets found, using environment variables")
            except Exception as e:
                print(f"Key Vault access failed: {e}, using environment variables")
        else:
            print("Key Vault not configured or in CI, using environment variables")

    AZURE_AI_ENDPOINT: str = ""
    AZURE_AGENT_ID: str = ""
    AZURE_CLIENT_ID: str = ""
    AZURE_CLIENT_SECRET: str = ""
    AZURE_TENANT_ID: str = ""
    AZURE_KEY_VAULT_ENDPOINT: str = ""
    API_ENVIRONMENT: str = ""

# Load settings from environment and key vault
settings = Settings()

# Global variables for lazy initialization
_client = None
_openai_endpoint = None
_agent_id = None

def _validate_and_parse_settings():
    """Lazy validation and parsing of settings"""
    global _openai_endpoint, _agent_id
    
    if _openai_endpoint is None:
        # Parse the base endpoint from the AI endpoint
        # AZURE_AI_ENDPOINT = "https://aif-instance-1.services.ai.azure.com/api/projects/aif-project-1"
        # We need: "https://aif-instance-1.openai.azure.com/"
        endpoint = settings.AZURE_AI_ENDPOINT
        if not endpoint:
            raise ValueError("AZURE_AI_ENDPOINT environment variable is not set")

        # Extract the instance name from the AI endpoint
        import re
        match = re.search(r'https://([^.]+)\.services\.ai\.azure\.com', endpoint)
        if not match:
            raise ValueError("Could not parse instance name from AZURE_AI_ENDPOINT")
        instance_name = match.group(1)

        # Build the OpenAI endpoint
        _openai_endpoint = f"https://{instance_name}.openai.azure.com/"
    
    if _agent_id is None:
        _agent_id = settings.AZURE_AGENT_ID
        if not _agent_id:
            raise ValueError("AZURE_AGENT_ID environment variable is not set")
    
    return _openai_endpoint, _agent_id

# Global variables for lazy initialization
_client = None

def get_openai_client():
    """Lazy initialization of AsyncAzureOpenAI client"""
    global _client
    if _client is None:
        try:
            openai_endpoint, agent_id = _validate_and_parse_settings()
            
            # Try service principal authentication first
            client_id = settings.AZURE_CLIENT_ID
            client_secret = settings.AZURE_CLIENT_SECRET
            tenant_id = settings.AZURE_TENANT_ID
            
            if client_id and client_secret and tenant_id:
                credential = ClientSecretCredential(
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret
                )
            else:
                credential = DefaultAzureCredential()
            
            # Get token for Cognitive Services
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            
            _client = AsyncAzureOpenAI(
                azure_endpoint=openai_endpoint,
                azure_ad_token=token.token,
                api_version="2024-02-15-preview"
            )
            
        except Exception as e:
            print(f"Failed to initialize AsyncAzureOpenAI client: {e}")
            raise
    return _client

async def chat_with_agent(user_message: str, conversation_history: Optional[List[Dict[str, str]]] = None, conversation_id: Optional[str] = None) -> dict:
    """
    Asynchronous function to chat with the OpenAI assistant with conversation history
    
    Args:
        user_message: The user's message
        conversation_history: List of previous messages in format [{"role": "user/assistant", "content": "message"}]
    
    Returns:
        Dict with response and conversation_id
    """
    # Check if we're in development mode or CI (no real Azure credentials)
    if settings.API_ENVIRONMENT == "develop" or not settings.AZURE_CLIENT_ID or settings.AZURE_CLIENT_ID == "your-client-id" or os.getenv('CI'):
        # Return a mock response for local development or CI
        return {
            "response": f"[DEV/CI MODE] I received your message: '{user_message}'. This is a mock response for local testing. To use real AI chat, configure your Azure credentials in Key Vault or environment variables.",
            "conversation_id": "dev-mode"
        }
    
    try:
        openai_endpoint, agent_id = _validate_and_parse_settings()
        client = get_openai_client()
        
        # Try to reuse existing thread if conversation_id is provided
        if conversation_id:
            try:
                # Check if the thread still exists
                existing_thread = await client.beta.threads.retrieve(thread_id=conversation_id)
                thread = existing_thread
                # Add the new message to existing thread
                await client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_message
                )
            except Exception:
                # Thread doesn't exist or is invalid, create new one
                print(f"Could not reuse thread {conversation_id}, creating new thread")
                thread = await client.beta.threads.create()
                # Add conversation history if provided
                if conversation_history:
                    for msg in conversation_history[-10:]:  # Limit to last 10 messages
                        role = msg["role"] if msg["role"] in ["user", "assistant"] else "user"
                        await client.beta.threads.messages.create(
                            thread_id=thread.id,
                            role=role,  # type: ignore
                            content=msg["content"]
                        )
                # Add the current user message
                await client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_message
                )
        else:
            # Create a new thread for the conversation
            thread = await client.beta.threads.create()
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-10:]:  # Limit to last 10 messages to avoid token limits
                    role = msg["role"] if msg["role"] in ["user", "assistant"] else "user"
                    await client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role=role,  # type: ignore
                        content=msg["content"]
                    )
            
            # Add the current user message
            await client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )
        
        # Create and run the assistant
        if not agent_id:
            raise ValueError("AZURE_AGENT_ID is not set")
            
        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=agent_id
        )
        
        # Wait for completion
        while run.status in ["queued", "in_progress"]:
            await asyncio.sleep(1)
            run = await client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            
        if run.status == "completed":
            # Get the latest assistant message
            messages = await client.beta.threads.messages.list(thread_id=thread.id, limit=1)
            for message in messages.data:
                if message.role == "assistant":
                    # Handle different content types safely
                    for content in message.content:
                        # Use type checking to safely access text content
                        if str(type(content).__name__) == 'TextContentBlock':
                            return {
                                "response": content.text.value,  # type: ignore
                                "conversation_id": thread.id
                            }
        
        return {
            "response": f"Run failed with status: {run.status}",
            "conversation_id": thread.id
        }
        
    except Exception as e:
        # If AI access fails but Key Vault is working, return a success message
        error_str = str(e)
        if "Key Vault" in error_str or "secrets" in error_str.lower():
            return {
                "response": f"[KEYVAULT WORKING] But AI access failed: {error_str}",
                "conversation_id": "error"
            }
        else:
            return {
                "response": f"[KEYVAULT SUCCESS] AI service error: {error_str}",
                "conversation_id": "error"
            }

# For standalone testing
if __name__ == "__main__":
    result = asyncio.run(chat_with_agent("คุณเป็นใคร"))
    print(f"Result: {result}")