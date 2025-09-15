import motor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import os
from pathlib import Path

# Use API_ALLOW_ORIGINS env var with comma separated urls like
# `http://localhost:300, http://otherurl:100`
# Requests coming to the api server from other urls will be rejected as per
# CORS.
allowOrigins = os.environ.get('API_ALLOW_ORIGINS')

# Use API_ENVIRONMENT to change webConfiguration based on this value.
# For example, setting API_ENVIRONMENT=develop disables CORS checking,
# allowing all origins.
environment = os.environ.get('API_ENVIRONMENT')

def originList():
    if environment is not None and environment == "develop":
        print("Allowing requests from any origins. API_ENVIRONMENT=", environment)
        return ["*"]
    
    origins = [
        "https://portal.azure.com",
        "https://ms.portal.azure.com",
    ]
    
    if allowOrigins is not None:
        for origin in allowOrigins.split(","):
            print("Allowing requests from", origin, ". To change or disable, go to ", Path(__file__))
            origins.append(origin)
        
    return origins
    
from .models import Settings, __beanie_models__

settings = Settings()

# Global variable to track initialization
_beanie_initialized = False

async def ensure_beanie_initialized():
    """Ensure Beanie is initialized before any database operations"""
    global _beanie_initialized
    if not _beanie_initialized:
        print("Initializing Beanie...")
        import motor.motor_asyncio
        client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.AZURE_COSMOS_CONNECTION_STRING
        )
        
        # Test the connection
        await client.admin.command('ping')
        print("Successfully pinged MongoDB server")
        
        database = client[settings.AZURE_COSMOS_DATABASE_NAME]
        print(f"Connected to database: {settings.AZURE_COSMOS_DATABASE_NAME}")
        
        await init_beanie(
            database=database,
            document_models=__beanie_models__,
        )
        print("Beanie initialization completed successfully")
        _beanie_initialized = True

app = FastAPI(
    description="The Globe API",
    version="3.0.0",
    title="The Globe API",
    docs_url="/",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=originList(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.APPLICATIONINSIGHTS_CONNECTION_STRING:
    exporter = AzureMonitorTraceExporter.from_connection_string(
        settings.APPLICATIONINSIGHTS_CONNECTION_STRING
    )
    tracerProvider = TracerProvider(
        resource=Resource({SERVICE_NAME: settings.APPLICATIONINSIGHTS_ROLENAME})
    )
    tracerProvider.add_span_processor(BatchSpanProcessor(exporter))

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracerProvider)


from . import routes  # NOQA

@app.get("/db-status")
async def db_status():
    """Check database connection status"""
    try:
        print(f"Testing database connection...")
        print(f"Connection string set: {bool(settings.AZURE_COSMOS_CONNECTION_STRING)}")
        print(f"Database name: {settings.AZURE_COSMOS_DATABASE_NAME}")
        
        # Create a simple motor client to test connection
        import motor.motor_asyncio
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.AZURE_COSMOS_CONNECTION_STRING)
        
        # Test connection with ping
        result = await client.admin.command('ping')
        print(f"Ping result: {result}")
        
        # Try to list databases
        db_list = await client.list_database_names()
        print(f"Available databases: {db_list}")
        
        # Check if our database exists
        db = client[settings.AZURE_COSMOS_DATABASE_NAME]
        collections = await db.list_collection_names()
        print(f"Collections in {settings.AZURE_COSMOS_DATABASE_NAME}: {collections}")
        
        return {
            "status": "connected", 
            "ping": result,
            "databases": db_list,
            "collections": collections
        }
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e), "type": type(e).__name__}

@app.on_event("startup")
async def startup_event():
    print(f"Starting database initialization...")
    print(f"Connection string set: {bool(settings.AZURE_COSMOS_CONNECTION_STRING)}")
    print(f"Database name: {settings.AZURE_COSMOS_DATABASE_NAME}")
    
    import motor.motor_asyncio
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.AZURE_COSMOS_CONNECTION_STRING
    )
    
    # Test the connection
    await client.admin.command('ping')
    print("Successfully pinged MongoDB server")
    
    database = client[settings.AZURE_COSMOS_DATABASE_NAME]
    print(f"Connected to database: {settings.AZURE_COSMOS_DATABASE_NAME}")
    
    await init_beanie(
        database=database,
        document_models=__beanie_models__,
    )
    print("Beanie initialization completed successfully")
