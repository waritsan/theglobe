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

@description('Cognitive Services account SKU name (e.g., S0, S1, etc.)')
param aiAccountSkuName string = 'S0'

@description('Assign a system-assigned managed identity to the Cognitive Services account')
param aiAssignIdentity bool = true

@description('Public network access setting for the Cognitive Services account')
@allowed([ 'Enabled', 'Disabled' ])
param publicNetworkAccess string = 'Enabled'

@description('Name of the model deployment resource')
param aiDeploymentName string = 'gpt4o-deploy'

@description('Model name to deploy (e.g., gpt-4o)')
param aiDeploymentModelName string = 'gpt-4o'

@description('Model publisher (e.g., OpenAI)')
param aiDeploymentPublisher string = 'OpenAI'

@description('Model format (required by deployment schema, e.g., OpenAI)')
param aiDeploymentModelFormat string = 'OpenAI'


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

// Model deployment (child resource of the Cognitive Services account)
resource aiDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = if (enabled) {
  name: aiDeploymentName
  parent: aiAccount
  sku : {
    capacity: 1
    name: 'GlobalStandard'
  }
  properties: {
    model: {
      name: aiDeploymentModelName
      publisher: aiDeploymentPublisher
      format: aiDeploymentModelFormat
    }
  }
}

output aiAccountName string = enabled ? aiAccount.name : ''
output aiAccountId string = enabled ? aiAccount.id : ''
// Construct endpoint from account name to avoid dereferencing the resource properties during compilation
output aiAccountEndpoint string = enabled ? 'https://${aiAccountName}.cognitiveservices.azure.com' : ''
output aiProjectId string = enabled ? aiProject.id : ''
output aiProjectName string = enabled ? aiProject.name : ''
output aiDeploymentName string = enabled ? aiDeployment.name : ''
output aiDeploymentId string = enabled ? aiDeployment.id : ''
output aiDeploymentModelName string = enabled ? aiDeploymentModelName : ''
