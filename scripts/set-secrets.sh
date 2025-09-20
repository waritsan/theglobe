#!/bin/bash
# Set secrets via Azure CLI (run after deployment)
# This script dynamically gets the Key Vault name from azd environment
# Usage: ./scripts/set-secrets.sh [environment-name]
# If no environment name is provided, it uses the current azd environment

set -e

# Allow overriding the environment name
ENV_NAME=${1:-$(azd env get-current)}

if [ -z "$ENV_NAME" ]; then
    echo "Error: No azd environment found. Please run 'azd init' first or specify environment name."
    exit 1
fi

echo "Using azd environment: $ENV_NAME"

# Get the Key Vault name from azd environment
KEYVAULT_NAME=$(azd env get-values --environment "$ENV_NAME" --output json | jq -r '.AZURE_KEY_VAULT_NAME')

if [ -z "$KEYVAULT_NAME" ] || [ "$KEYVAULT_NAME" = "null" ]; then
    echo "Error: Could not get Key Vault name from azd environment '$ENV_NAME'"
    echo "Make sure you have run 'azd provision' first"
    exit 1
fi

echo "Setting secrets in Key Vault: $KEYVAULT_NAME"

# Check if secrets are provided as environment variables, otherwise use placeholders
AI_ENDPOINT=${AZURE_AI_ENDPOINT:-"YOUR_AI_ENDPOINT"}
AGENT_ID=${AZURE_AGENT_ID:-"YOUR_AGENT_ID"}
CLIENT_ID=${AZURE_CLIENT_ID:-"YOUR_CLIENT_ID"}
CLIENT_SECRET=${AZURE_CLIENT_SECRET:-"YOUR_CLIENT_SECRET"}
TENANT_ID=${AZURE_TENANT_ID:-"YOUR_TENANT_ID"}

# Set the secrets
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name azure-ai-endpoint --value "$AI_ENDPOINT"
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name azure-agent-id --value "$AGENT_ID"
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name azure-client-id --value "$CLIENT_ID"
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name azure-client-secret --value "$CLIENT_SECRET"
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name azure-tenant-id --value "$TENANT_ID"

echo "Secrets set successfully in Key Vault: $KEYVAULT_NAME"
echo ""
echo "Next steps:"
echo "1. Update the placeholder values with your actual Azure AI credentials"
echo "2. Run: azd deploy"
echo ""
echo "Or set environment variables before running:"
echo "export AZURE_AI_ENDPOINT='your-endpoint'"
echo "export AZURE_AGENT_ID='your-agent-id'"
echo "# ... etc"
echo "./scripts/set-secrets.sh"