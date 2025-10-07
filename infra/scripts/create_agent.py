#!/usr/bin/env python3
"""Create AI agent in AI Projects and persist its ID to Key Vault and local .env.

This script is intended to run during `azd up` where environment variables
for AI endpoint, subscription, resource group, and project are available.

It performs:
- create AIProjectClient
- ensure an agent exists (uses AZURE_MODEL for model name)
- persist the agent id to Key Vault secret named 'azure-agent-id'
- write agent id to local .azure/dev/.env (or env file provided by AZD)

This script does best-effort error handling and prints outcomes for azd logs.
"""
import os
import sys
import logging

try:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.keyvault.secrets import SecretClient
except Exception:
    print("Required Azure SDKs are not installed in the environment. Skipping agent creation.")
    sys.exit(0)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("create-agent")

# Load config from environment that azd sets during provision
endpoint = os.getenv("AZURE_AI_ENDPOINT") or os.getenv("AI_FOUNDRY_ACCOUNT_ENDPOINT") or os.getenv("PROJECT_ENDPOINT")
subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
resource_group = os.getenv("AZURE_RESOURCE_GROUP_NAME") or os.getenv("AZURE_RESOURCE_GROUP")
project_name = os.getenv("AZURE_AI_PROJECT_NAME") or os.getenv("AI_FOUNDRY_PROJECT_NAME")
model_name = os.getenv("AZURE_MODEL")
kv_endpoint = os.getenv("AZURE_KEY_VAULT_ENDPOINT")

if not endpoint or not subscription_id or not resource_group or not project_name or not model_name:
    log.info("Missing AI project configuration (endpoint/subscription/resource-group/project/model). Skipping agent creation.")
    sys.exit(0)

# Build credential
def _build_credential():
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    if client_id and client_secret and tenant_id:
        return ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    return DefaultAzureCredential()

cred = _build_credential()

# Create project client
try:
    client = AIProjectClient(credential=cred, endpoint=endpoint)
except Exception as e:
    # SDK variations
    base_endpoint = endpoint.split("/api/projects/")[0] if "/api/projects/" in endpoint else endpoint
    client = AIProjectClient(credential=cred, endpoint=base_endpoint, subscription_id=subscription_id, resource_group_name=resource_group, project_name=project_name)

# Try to load existing agent id from keyvault if available
agent_id = None
if kv_endpoint:
    try:
        kv = SecretClient(vault_url=kv_endpoint, credential=cred)
        sec = kv.get_secret("azure-agent-id")
        agent_id = sec.value
        log.info("Loaded agent id from Key Vault: %s", agent_id)
    except Exception:
        log.info("No azure-agent-id secret present in Key Vault (or access denied).")

# Validate existing agent id
if agent_id:
    try:
        client.agents.get_agent(agent_id)
        log.info("Agent already exists (id=%s). Nothing to do.", agent_id)
    except Exception:
        log.info("Agent id from KV not valid; will create a new agent.")
        agent_id = None

# Create agent if none
if not agent_id:
    log.info("Creating agent using model=%s", model_name)
    a = client.agents.create_agent(model=model_name, name="The Globe Assistant", instructions="You are The Globe's helpful assistant.")
    agent_id = a.id
    log.info("Created agent id=%s", agent_id)
    # Persist to keyvault if available
    if kv_endpoint:
        try:
            kv.set_secret("azure-agent-id", agent_id)
            log.info("Persisted agent id to Key Vault")
        except Exception as ex:
            log.warning("Failed to persist agent id to Key Vault: %s", ex)

# Write to local env file used by azd (if exists), fallback to .azure/dev/.env
env_path = os.getenv("AZD_ENV_FILE") or os.path.join(os.getcwd(), ".azure", "dev", ".env")
try:
    # Ensure directory
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    # Append or create
    with open(env_path, "a") as f:
        f.write(f"AZURE_AGENT_ID=\"{agent_id}\"\n")
    log.info("Wrote AZURE_AGENT_ID to %s", env_path)
except Exception as ex:
    log.warning("Failed to write agent id to local env file: %s", ex)

print(agent_id)
