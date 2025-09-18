import os
import json
import asyncio
from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, ClientSecretCredential

# Load environment variables from local.settings.json if not already set
settings_path = os.path.join(os.path.dirname(__file__), '..', 'local.settings.json')
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        settings = json.load(f)
        values = settings.get('Values', {})
        
        # Force set all required environment variables
        required_vars = [
            'AZURE_AI_ENDPOINT', 'AZURE_AGENT_ID', 'AZURE_SUBSCRIPTION_ID', 
            'AZURE_RESOURCE_GROUP_NAME', 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET', 'AZURE_TENANT_ID'
        ]
        
        for var in required_vars:
            if var in values and values[var]:
                os.environ[var] = values[var]

# Parse the base endpoint from the AI endpoint
# AZURE_AI_ENDPOINT = "https://aif-instance-1.services.ai.azure.com/api/projects/aif-project-1"
# We need: "https://aif-instance-1.openai.azure.com/"
endpoint = os.environ.get('AZURE_AI_ENDPOINT')
if not endpoint:
    raise ValueError("AZURE_AI_ENDPOINT environment variable is not set")

# Extract the instance name from the AI endpoint
import re
match = re.search(r'https://([^.]+)\.services\.ai\.azure\.com', endpoint)
if not match:
    raise ValueError("Could not parse instance name from AZURE_AI_ENDPOINT")
instance_name = match.group(1)

# Build the OpenAI endpoint
openai_endpoint = f"https://{instance_name}.openai.azure.com/"

agent_id = os.environ.get('AZURE_AGENT_ID')
if not agent_id:
    raise ValueError("AZURE_AGENT_ID environment variable is not set")

# Global variables for lazy initialization
_client = None

def get_openai_client():
    """Lazy initialization of AsyncAzureOpenAI client"""
    global _client
    if _client is None:
        try:
            # Try service principal authentication first
            client_id = os.environ.get('AZURE_CLIENT_ID')
            client_secret = os.environ.get('AZURE_CLIENT_SECRET')
            tenant_id = os.environ.get('AZURE_TENANT_ID')
            
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
    try:
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
        return f"Error: {str(e)}"

# For standalone testing
if __name__ == "__main__":
    result = asyncio.run(chat_with_agent("คุณเป็นใคร"))
    print(f"Result: {result}")