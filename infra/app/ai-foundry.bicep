targetScope = 'resourceGroup'

@description('Cognitive Services account name')
param aiAccountName string

@description('Deployment location')
param location string

@description('Resource tags')
param tags object = {}

@description('AI Foundry project resource name')
param aiProjectName string

@description('Display name for the AI Foundry project')
param aiProjectDisplayName string = 'The Globe AI'

@description('Description for the AI Foundry project')
param aiProjectDescription string = 'AI Foundry project for The Globe application'

@description('Cognitive Services account kind. Use AIServices for Azure AI Foundry projects, or OpenAI for Azure OpenAI accounts')
param aiAccountKind string = 'AIServices'

@description('SKU name for the Cognitive Services account')
param aiAccountSkuName string = 'S0'

@description('Assign a system-assigned managed identity to the Cognitive Services account')
param aiAssignIdentity bool = true

@description('Public network access setting for the Cognitive Services account')
@allowed([ 'Enabled', 'Disabled' ])
param publicNetworkAccess string = 'Enabled'

resource aiAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: aiAccountName
  kind: aiAccountKind
  location: location
  tags: tags
  sku: {
    name: aiAccountSkuName
  }
  identity: {
    type: aiAssignIdentity ? 'SystemAssigned' : 'None'
  }
  properties: {
    publicNetworkAccess: publicNetworkAccess
    allowProjectManagement: true 
    customSubDomainName: aiAccountName
  }
}

resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  name: aiProjectName
  parent: aiAccount
  tags: tags
  location: location
  identity: {
    type: aiAssignIdentity ? 'SystemAssigned' : 'None'
  }
  properties: {
    displayName: aiProjectDisplayName
    description: aiProjectDescription
  }
}

output aiAccountName string = aiAccount.name
output aiAccountId string = aiAccount.id
output aiAccountEndpoint string = aiAccount.properties.endpoint
output aiProjectId string = aiProject.id
output aiProjectName string = aiProject.name
