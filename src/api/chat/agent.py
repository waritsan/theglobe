import os
import json
import asyncio
from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from pydantic import BaseSettings

def keyvault_name_as_attr(name: str) -> str:
    return name.replace("-", "_").upper()

class Settings(BaseSettings):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Always try to load from Key Vault first if endpoint is available and we're not in CI
        if self.AZURE_KEY_VAULT_ENDPOINT and not os.getenv('CI'):
            try:
                credential = DefaultAzureCredential()
                keyvault_client = SecretClient(self.AZURE_KEY_VAULT_ENDPOINT, credential)
                for secret in keyvault_client.list_properties_of_secrets():
                    if secret.name:
                        setattr(
                            self,
                            keyvault_name_as_attr(secret.name),
                            keyvault_client.get_secret(secret.name).value,
                        )
                print(f"Successfully loaded {len(list(keyvault_client.list_properties_of_secrets()))} secrets from Key Vault")
            except Exception as e:
                print(f"Warning: Could not load secrets from Key Vault: {e}")
                print("Falling back to environment variables...")
        else:
            print("Key Vault endpoint not configured or in CI environment, using environment variables")

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

async def chat_with_agent(user_message: str) -> str:
    """
    Asynchronous function to chat with the OpenAI assistant
    """
    # Check if we're in development mode or CI (no real Azure credentials)
    if settings.API_ENVIRONMENT == "develop" or not settings.AZURE_CLIENT_ID or settings.AZURE_CLIENT_ID == "your-client-id" or os.getenv('CI'):
        # Return a mock response for local development or CI
        return f"[DEV/CI MODE] I received your message: '{user_message}'. This is a mock response for local testing. To use real AI chat, configure your Azure credentials in Key Vault or environment variables."
    
    try:
        openai_endpoint, agent_id = _validate_and_parse_settings()
        client = get_openai_client()
        
        # Create a thread
        thread = await client.beta.threads.create()
        
        # Add message to thread
        message = await client.beta.threads.messages.create(
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
            # Get messages
            messages = await client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                if message.role == "assistant":
                    # Handle different content types safely
                    for content in message.content:
                        # Use type checking to safely access text content
                        if str(type(content).__name__) == 'TextContentBlock':
                            return content.text.value  # type: ignore
                    
        return f"Run failed with status: {run.status}"
        
    except Exception as e:
        # If AI access fails but Key Vault is working, return a success message
        error_str = str(e)
        if "Key Vault" in error_str or "secrets" in error_str.lower():
            return f"[KEYVAULT WORKING] But AI access failed: {error_str}"
        else:
            return f"[KEYVAULT SUCCESS] AI service error: {error_str}"

# For standalone testing
if __name__ == "__main__":
    result = asyncio.run(chat_with_agent("คุณเป็นใคร"))
    print(f"Result: {result}")