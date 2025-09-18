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

async def list_assistants():
    """List all available assistants"""
    try:
        # Get credentials
        client_id = os.environ.get('AZURE_CLIENT_ID')
        client_secret = os.environ.get('AZURE_CLIENT_SECRET')
        tenant_id = os.environ.get('AZURE_TENANT_ID')
        
        if client_id and client_secret and tenant_id:
            print("Using ClientSecretCredential (Service Principal)")
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        else:
            print("Using DefaultAzureCredential (Azure CLI)")
            credential = DefaultAzureCredential()
        
        # Get token for Cognitive Services
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        print(f"Successfully obtained token")
        
        client = AsyncAzureOpenAI(
            azure_endpoint=openai_endpoint,
            azure_ad_token=token.token,
            api_version="2024-02-15-preview"
        )
        
        print(f"Listing assistants from: {openai_endpoint}")
        assistants = await client.beta.assistants.list()
        
        print(f"Found {len(assistants.data)} assistants:")
        for assistant in assistants.data:
            print(f"  ID: {assistant.id}")
            print(f"  Name: {assistant.name}")
            print(f"  Description: {assistant.description}")
            print(f"  Created: {assistant.created_at}")
            print("  ---")
            
        return assistants.data
        
    except Exception as e:
        print(f"Error listing assistants: {e}")
        print(f"Error type: {type(e).__name__}")
        return []

if __name__ == "__main__":
    assistants = asyncio.run(list_assistants())