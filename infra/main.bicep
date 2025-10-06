targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

// Optional parameters to override the default azd resource naming conventions. Update the main.parameters.json file to provide values. e.g.,:
// "resourceGroupName": {
//      "value": "myGroupName"
// }
param apiServiceName string = ''
param applicationInsightsDashboardName string = ''
param applicationInsightsName string = ''
param appServicePlanName string = ''
param cosmosAccountName string = ''
param keyVaultName string = ''
param logAnalyticsName string = ''
param resourceGroupName string = ''
param storageAccountName string = ''
param webServiceName string = ''
param apimServiceName string = ''

// Azure AI Foundry (Cognitive Services) params
@description('Set to true to deploy an Azure AI (Cognitive Services) account and an AI Foundry Project')
param deployAIFoundry bool = true

@description('Cognitive Services account name; leave empty to auto-generate')
param aiAccountName string = ''

@description('AI Foundry project resource name; leave empty to auto-generate')
param aiProjectName string = ''

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

@description('Flag to use Azure API Management to mediate the calls between the Web frontend and the backend API')
param useAPIM bool = false

@description('API Management SKU to use if APIM is enabled')
param apimSku string = 'Consumption'

@description('Id of the user or app to assign application roles')
param principalId string = ''

var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }
var webUri = 'https://${web.outputs.defaultHostname}'
var apimResolvedName = !empty(apimServiceName) ? apimServiceName : '${abbrs.apiManagementService}${resourceToken}'

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// The application frontend
module web 'br/public:avm/res/web/static-site:0.3.0' = {
  name: 'staticweb'
  scope: rg
  params: {
    name: !empty(webServiceName) ? webServiceName : '${abbrs.webStaticSites}web-${resourceToken}'
    location: location
    provider: 'Custom'
    tags: union(tags, { 'azd-service-name': 'web' })
  }
}

// The application backend
module api './app/api-appservice-avm.bicep' = {
  name: 'api'
  scope: rg
  params: {
    name: !empty(apiServiceName) ? apiServiceName : '${abbrs.webSitesAppService}api-${resourceToken}'
    location: location
    tags: tags
    kind: 'functionapp'
    appServicePlanId: appServicePlan.outputs.resourceId
    appSettings: {
      API_ALLOW_ORIGINS: webUri
      AZURE_COSMOS_CONNECTION_STRING_KEY: cosmos.outputs.connectionStringKey
      AZURE_COSMOS_DATABASE_NAME: cosmos.outputs.databaseName
      AZURE_KEY_VAULT_ENDPOINT:keyVault.outputs.uri
      AZURE_COSMOS_ENDPOINT: 'https://${cosmos.outputs.databaseName}.documents.azure.com:443/'
      FUNCTIONS_EXTENSION_VERSION: '~4'
      FUNCTIONS_WORKER_RUNTIME: 'python'
      SCM_DO_BUILD_DURING_DEPLOYMENT: true
    }
    appInsightResourceId: monitoring.outputs.applicationInsightsResourceId
    siteConfig: {
      linuxFxVersion: 'python|3.10'
    }
    allowedOrigins: [ webUri ]
    storageAccountResourceId: storage.outputs.resourceId
    clientAffinityEnabled: false
  }
}

// Give the API access to KeyVault
module accessKeyVault 'br/public:avm/res/key-vault/vault:0.5.1' = {
  name: 'accesskeyvault'
  scope: rg
  params: {
    name: keyVault.outputs.name
    enableRbacAuthorization: false
    enableVaultForDeployment: false
    enableVaultForTemplateDeployment: false
    enablePurgeProtection: false
    sku: 'standard'
    accessPolicies: [
      {
        objectId: api.outputs.SERVICE_API_IDENTITY_PRINCIPAL_ID
        permissions: {
          secrets: [ 'get', 'list' ]
        }
      }
      {
        objectId: principalId
        permissions: {
          secrets: [ 'get', 'list' ]
        }
      }
    ]
  }
}

// The application database
module cosmos './app/db-avm.bicep' = {
  name: 'cosmos'
  scope: rg
  params: {
    accountName: !empty(cosmosAccountName) ? cosmosAccountName : '${abbrs.documentDBDatabaseAccounts}${resourceToken}'
    location: location
    tags: tags
    keyVaultResourceId: keyVault.outputs.resourceId
  }
}

// Create an App Service Plan to group applications under the same payment plan and SKU
module appServicePlan 'br/public:avm/res/web/serverfarm:0.1.1' = {
  name: 'appserviceplan'
  scope: rg
  params: {
    name: !empty(appServicePlanName) ? appServicePlanName : '${abbrs.webServerFarms}${resourceToken}'
    sku: {
      name: 'Y1'
      tier: 'Dynamic'
    }
    location: location
    tags: tags
    reserved: true
    kind: 'Linux'
  }
}

// Backing storage for Azure functions backend API
module storage 'br/public:avm/res/storage/storage-account:0.8.3' = {
  name: 'storage'
  scope: rg
  params: {
    name: !empty(storageAccountName) ? storageAccountName : '${abbrs.storageStorageAccounts}${resourceToken}'
    allowBlobPublicAccess: true
    dnsEndpointType: 'Standard'
    publicNetworkAccess:'Enabled'
    networkAcls:{
      bypass: 'AzureServices'
      defaultAction: 'Allow'
    }
    location: location
    tags: tags
  }
}

// Create a keyvault to store secrets
module keyVault 'br/public:avm/res/key-vault/vault:0.5.1' = {
  name: 'keyvault'
  scope: rg
  params: {
    name: !empty(keyVaultName) ? keyVaultName : '${abbrs.keyVaultVaults}${resourceToken}'
    location: location
    tags: tags
    enableRbacAuthorization: false
    enableVaultForDeployment: false
    enableVaultForTemplateDeployment: false
    enablePurgeProtection: false
    sku: 'standard'
  }
}

// Azure AI Foundry resources (Cognitive Services account + Project)
module aiFoundry './app/ai-foundry.bicep' = {
  name: 'ai-foundry'
  scope: rg
  params: {
    enabled: deployAIFoundry
    aiAccountName: !empty(aiAccountName) ? aiAccountName : '${abbrs.cognitiveServicesAccounts}${resourceToken}'
    aiProjectName: !empty(aiProjectName) ? aiProjectName : 'aiproj-${resourceToken}'
    location: location
    tags: tags
    aiAccountKind: aiAccountKind
    aiAccountSkuName: aiAccountSkuName
    aiAssignIdentity: aiAssignIdentity
    aiProjectDisplayName: aiProjectDisplayName
    aiProjectDescription: aiProjectDescription
  }
}

// Monitor application with Azure Monitor
module monitoring 'br/public:avm/ptn/azd/monitoring:0.1.0' = {
  name: 'monitoring'
  scope: rg
  params: {
    applicationInsightsName: !empty(applicationInsightsName) ? applicationInsightsName : '${abbrs.insightsComponents}${resourceToken}'
    logAnalyticsName: !empty(logAnalyticsName) ? logAnalyticsName : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsDashboardName: !empty(applicationInsightsDashboardName) ? applicationInsightsDashboardName : '${abbrs.portalDashboards}${resourceToken}'
    location: location
    tags: tags
  }
}

// Creates Azure API Management (APIM) service to mediate the requests between the frontend and the backend API
module apim 'br/public:avm/res/api-management/service:0.2.0' = if (useAPIM) {
  name: 'apim-deployment'
  scope: rg
  params: {
    name: apimResolvedName
    publisherEmail: 'noreply@microsoft.com'
    publisherName: 'n/a'
    location: location
    tags: tags
    sku: apimSku
    skuCount: 0
    zones: []
    customProperties: {}
    loggers: [
      {
        name: 'app-insights-logger'
        credentials: {
          instrumentationKey: monitoring.outputs.applicationInsightsInstrumentationKey
        }
        loggerDescription: 'Logger to Azure Application Insights'
        isBuffered: false
        loggerType: 'applicationInsights'
        targetResourceId: monitoring.outputs.applicationInsightsResourceId
      }
    ]
  }
}

//Configures the API settings for an api app within the Azure API Management (APIM) service.
module apimApi 'br/public:avm/ptn/azd/apim-api:0.1.0' = if (useAPIM) {
  name: 'apim-api-deployment'
  scope: rg
  params: {
    apiBackendUrl: api.outputs.SERVICE_API_URI
    apiDescription: 'The Globe Blog API'
    apiDisplayName: 'The Globe API'
    apiName: 'theglobe-api'
    apiPath: 'blog'
  name: apimResolvedName
    webFrontendUrl: webUri
    location: location
    apiAppName: api.outputs.SERVICE_API_NAME
  }
}

// Data outputs
output AZURE_COSMOS_CONNECTION_STRING_KEY string = cosmos.outputs.connectionStringKey
output AZURE_COSMOS_DATABASE_NAME string = cosmos.outputs.databaseName

// App outputs
output APPLICATIONINSIGHTS_CONNECTION_STRING string = monitoring.outputs.applicationInsightsConnectionString
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.uri
output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output API_BASE_URL string = api.outputs.SERVICE_API_URI
output REACT_APP_WEB_BASE_URL string = webUri
output USE_APIM bool = useAPIM
output SERVICE_API_ENDPOINTS array = []

// Azure AI Foundry outputs
output AI_FOUNDRY_ACCOUNT_NAME string = aiFoundry.outputs.aiAccountName
output AI_FOUNDRY_ACCOUNT_ID string = aiFoundry.outputs.aiAccountId
output AI_FOUNDRY_ACCOUNT_ENDPOINT string = aiFoundry.outputs.aiAccountEndpoint
output AI_FOUNDRY_PROJECT_ID string = aiFoundry.outputs.aiProjectId
output AI_FOUNDRY_PROJECT_NAME string = aiFoundry.outputs.aiProjectName
output AI_FOUNDRY_DEPLOYMENT_MODEL_NAME string = aiFoundry.outputs.aiDeploymentModelName
