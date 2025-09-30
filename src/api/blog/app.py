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
from dotenv import load_dotenv
from dotenv import load_dotenv

# Load environment variables from .env so dev flags like API_ENVIRONMENT are applied
load_dotenv()

# Load environment variables from .env if present (for local dev convenience)
load_dotenv()

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
            origin = origin.strip()
            if origin:
                print("Allowing requests from", origin, ". To change or disable, go to ", Path(__file__))
                origins.append(origin)

    # Always include common local dev origins if not in develop but explicitly allowed via env
    print("CORS allowed origins:", origins)
    return origins
    
from .models import Settings, __beanie_models__

settings = Settings()

# Global variable to track initialization
_beanie_initialized = False

def create_motor_client(conn_str: str):
    """Create a Motor client. Enable TLS when requested in the connection string.

    The connection string can include `tls=false` (or `ssl=false`) for local
    non-TLS MongoDB instances (useful in CI). When TLS is enabled, the certifi
    CA bundle is used for verification.
    """
    import motor.motor_asyncio
    import certifi

    # If no connection string is provided, default to a local MongoDB
    # instance without TLS. Calling Motor/pymongo with an empty connection
    # string raises ConfigurationError (empty host), which we saw in logs.
    if not conn_str:
        print("AZURE_COSMOS_CONNECTION_STRING is empty; defaulting to 'mongodb://localhost:27017/?tls=false'")
        conn_str = "mongodb://localhost:27017/?tls=false"

    # Default to using TLS. If the connection string explicitly disables TLS
    # (e.g. `mongodb://localhost:27017/?tls=false`) then turn it off so a
    # local, non-TLS mongod can be used in CI.
    use_tls = True
    if conn_str:
        low = conn_str.lower()
        if 'tls=false' in low or 'ssl=false' in low:
            use_tls = False

    if use_tls:
        return motor.motor_asyncio.AsyncIOMotorClient(
            conn_str,
            tls=True,
            tlsCAFile=certifi.where()
        )
    else:
        return motor.motor_asyncio.AsyncIOMotorClient(
            conn_str,
            tls=False
        )

async def ensure_beanie_initialized():
    """Ensure Beanie is initialized before any database operations"""
    global _beanie_initialized
    if not _beanie_initialized:
        print("Initializing Beanie...")
        client = create_motor_client(settings.AZURE_COSMOS_CONNECTION_STRING)
        
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
    role_name = settings.APPLICATIONINSIGHTS_ROLENAME or "theglobe-api"
    tracerProvider = TracerProvider(
        resource=Resource({SERVICE_NAME: role_name})
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

        client = create_motor_client(settings.AZURE_COSMOS_CONNECTION_STRING)

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
            "collections": collections,
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
    
    client = create_motor_client(settings.AZURE_COSMOS_CONNECTION_STRING)

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
