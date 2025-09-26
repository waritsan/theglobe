import os
import sys
import asyncio
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

async def main():
    kv_endpoint = os.getenv('AZURE_KEY_VAULT_ENDPOINT')
    secret_name = os.getenv('AZURE_COSMOS_CONNECTION_STRING_KEY', 'AZURE-COSMOS-CONNECTION-STRING')
    db_name = os.getenv('AZURE_COSMOS_DATABASE_NAME', 'Blog')

    if not kv_endpoint:
        print('AZURE_KEY_VAULT_ENDPOINT not set')
        sys.exit(1)

    try:
        cred = DefaultAzureCredential()
        client = SecretClient(vault_url=kv_endpoint, credential=cred)
        secret = client.get_secret(secret_name)
        conn_str = secret.value
        print('Fetched secret from Key Vault')
    except Exception as e:
        print('Failed to get secret from Key Vault:', e)
        sys.exit(1)

    try:
        import motor.motor_asyncio
        client = motor.motor_asyncio.AsyncIOMotorClient(conn_str)
        db = client[db_name]
        cols = await db.list_collection_names()
        print('Connected to DB:', db_name)
        print('Collections:', cols)
    except Exception as e:
        print('Failed to connect to Cosmos/Mongo:', e)
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
