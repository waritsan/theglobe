import logging
import azure.functions as func
from azure.functions._http_asgi import AsgiResponse, AsgiRequest
from todo import app  # Main API application module (todo/app.py)

logger = logging.getLogger(__name__)
initialized = False

async def ensure_init(app_module):
    """Ensure the FastAPI app has initialized database and other resources.
    Azure Functions may not trigger ASGI lifespan, so we explicitly call our
    module-provided startup initializer once per cold start.
    """
    global initialized
    if initialized:
        return
    try:
        await app_module.startup_event()
        initialized = True
        logger.info("Application initialization completed")
    except Exception as exc:
        logger.exception("Application initialization failed: %s", exc)
        # Re-raise so caller can produce a 500 response
        raise

async def handle_asgi_request(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    try:
        asgi_request = AsgiRequest(req, context)
        scope = asgi_request.to_asgi_http_scope()
        asgi_response = await AsgiResponse.from_app(app.app, scope, req.get_body())
        return asgi_response.to_func_response()
    except Exception as exc:
        logger.exception("Unhandled exception in request handling: %s", exc)
        return func.HttpResponse(
            status_code=500,
            body=b"Internal Server Error",
            mimetype="text/plain",
        )

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    try:
        await ensure_init(app)
    except Exception:
        # Return a clear 500 if init fails; logs will contain the stack trace
        return func.HttpResponse(
            status_code=500,
            body=b"Initialization failed. Check application logs for details.",
            mimetype="text/plain",
        )
    return await handle_asgi_request(req, context)
