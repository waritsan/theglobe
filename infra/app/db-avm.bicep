param accountName string
param location string = resourceGroup().location
param tags object = {}
param cosmosDatabaseName string = ''
param keyVaultResourceId string
param connectionStringKey string = 'AZURE-COSMOS-CONNECTION-STRING'
param collections array = [
  {
    name: 'BlogPost'
    id: 'BlogPost'
    shardKey: {
      keys: [
        'Hash'
      ]
    }
    indexes: [
      {
        key: {
          keys: [
            '_id'
          ]
        }
      }
    ]
  }
  {
    name: 'Comment'
    id: 'Comment'
    shardKey: {
      keys: [
        'Hash'
      ]
    }
    indexes: [
      {
        key: {
          keys: [
            '_id'
          ]
        }
      }
    ]
  }
]

var defaultDatabaseName = 'Blog'
var actualDatabaseName = !empty(cosmosDatabaseName) ? cosmosDatabaseName : defaultDatabaseName

// Enable Cosmos DB Free Tier and serverless capability by default. These can be
// overridden when the module is called from higher-level templates.
param enableFreeTier bool = true
param enableServerless bool = true

module cosmos 'br/public:avm/res/document-db/database-account:0.6.0' = {
  name: 'cosmos-mongo'
  params: {
    locations: [
      {
        failoverPriority: 0
        isZoneRedundant: false
        locationName: location
      }
    ]
    name: accountName
    location: location
    mongodbDatabases: [
      {
        name: actualDatabaseName
        tags: tags
        collections: collections
      }
    ]
    // Add serverless capability when requested. The AVM module accepts
    // `capabilitiesToAdd` and `enableFreeTier` which map to ARM properties
    // that enable serverless and free-tier features respectively.
    capabilitiesToAdd: enableServerless ? [ 'EnableServerless' ] : []
    enableFreeTier: enableFreeTier
    secretsExportConfiguration: {
      keyVaultResourceId: keyVaultResourceId
      primaryWriteConnectionStringSecretName: connectionStringKey
    }
  }
}

output connectionStringKey string = connectionStringKey
output databaseName string = actualDatabaseName
output endpoint string = cosmos.outputs.endpoint
