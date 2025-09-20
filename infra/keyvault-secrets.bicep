targetScope = 'resourceGroup'

@description('Name of the Key Vault')
param keyVaultName string

@description('AI Foundry endpoint URL')
param aiEndpoint string

@description('Azure OpenAI Assistant ID')
param agentId string

@description('Service Principal Client ID')
param clientId string

@description('Service Principal Client Secret')
@secure()
param clientSecret string

@description('Azure Tenant ID')
param tenantId string

// Add secrets to the existing Key Vault
resource aiEndpointSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: '${keyVaultName}/azure-ai-endpoint'
  properties: {
    value: aiEndpoint
  }
}

resource agentIdSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: '${keyVaultName}/azure-agent-id'
  properties: {
    value: agentId
  }
}

resource clientIdSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: '${keyVaultName}/azure-client-id'
  properties: {
    value: clientId
  }
}

resource clientSecretSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: '${keyVaultName}/azure-client-secret'
  properties: {
    value: clientSecret
  }
}

resource tenantIdSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: '${keyVaultName}/azure-tenant-id'
  properties: {
    value: tenantId
  }
}
