import azure.functions as func
from azure.functions._http_asgi import AsgiResponse, AsgiRequest
import sys
import os
import logging

logger = logging.getLogger(__name__)

# Ensure the parent directory is on path to import the blog package
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the Blog API module (module contains FastAPI app and init functions)
import blog.app as blog_app_module

initialized = False

async def ensure_init():
    global initialized
    if initialized:
        return
    # Azure Functions may not trigger FastAPI lifespan; explicitly initialize DB/Beanie
    try:
        if hasattr(blog_app_module, "startup_event"):
            await blog_app_module.startup_event()
        elif hasattr(blog_app_module, "ensure_beanie_initialized"):
            await blog_app_module.ensure_beanie_initialized()
        initialized = True
        logger.info("Blog API initialization completed")
    except Exception:
        logger.exception("Blog API initialization failed")
        raise

async def handle_asgi_request(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    asgi_request = AsgiRequest(req, context)
    scope = asgi_request.to_asgi_http_scope()
    asgi_response = await AsgiResponse.from_app(blog_app_module.app, scope, req.get_body())
    return asgi_response.to_func_response()

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    # Determine the request path from route params or URL
    route_param = req.route_params.get('route') if hasattr(req, 'route_params') else None
    path = route_param or '/'
    if not path.startswith('/'):
        path = f'/{path}'

    # Allow health and docs to work without forcing DB init
    skip_init = path == '/health' or path == '/' or path.startswith('/docs') or path.startswith('/openapi') or path.startswith('/static')

    if not skip_init:
        try:
            await ensure_init()
        except Exception:
            return func.HttpResponse(
                status_code=500,
                body=b"Initialization failed. Check application logs for details.",
                mimetype="text/plain",
            )

    return await handle_asgi_request(req, context)
