param accountName string
param location string = resourceGroup().location
param tags object = {}
param cosmosDatabaseName string = ''
param keyVaultResourceId string
param connectionStringKey string = 'AZURE-COSMOS-CONNECTION-STRING'
param collections array = [
  {
    name: 'Category'
    id: 'Category'
    shardKey: {
      keys: [ 'Hash' ]
    }
    indexes: [
      {
        key: {
          keys: [ '_id' ]
        }
      }
    ]
  }
  {
    name: 'BlogPost'
    id: 'BlogPost'
    shardKey: {
      keys: [ 'Hash' ]
    }
    indexes: [
      {
        key: {
          keys: [ '_id' ]
        }
      }
    ]
  }
  {
    name: 'Comment'
    id: 'Comment'
    shardKey: {
      keys: [ 'Hash' ]
    }
    indexes: [
      {
        key: {
          keys: [ '_id' ]
        }
      }
    ]
  }
]

var defaultDatabaseName = 'Blog'
var actualDatabaseName = !empty(cosmosDatabaseName) ? cosmosDatabaseName : defaultDatabaseName

module cosmos 'br/public:avm/res/document-db/database-account:0.6.0' = {
  name: 'cosmos-mongo'
  params: {
    enableFreeTier: true
    capabilitiesToAdd: [
      'EnableServerless'
    ]
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
    secretsExportConfiguration: {
      keyVaultResourceId: keyVaultResourceId
      primaryWriteConnectionStringSecretName: connectionStringKey
    }
  }
}

output connectionStringKey string = connectionStringKey
output databaseName string = actualDatabaseName
output endpoint string = cosmos.outputs.endpoint
