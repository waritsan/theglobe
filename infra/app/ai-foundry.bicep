targetScope = 'resourceGroup'

@description('Cognitive Services account name')
param aiAccountName string

@description('Deployment location')
param location string

@description('Enable deployment of AI Foundry resources')
param enabled bool = true

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

resource aiAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' = if (enabled) {
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

resource aiProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = if (enabled) {
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

output aiAccountName string = enabled ? aiAccount.name : ''
output aiAccountId string = enabled ? aiAccount.id : ''
// Construct endpoint from account name to avoid dereferencing the resource properties during compilation
output aiAccountEndpoint string = enabled ? 'https://${aiAccountName}.cognitiveservices.azure.com' : ''
output aiProjectId string = enabled ? aiProject.id : ''
output aiProjectName string = enabled ? aiProject.name : ''
