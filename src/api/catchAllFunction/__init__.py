import azure.functions as func
from azure.functions._http_asgi import AsgiResponse, AsgiRequest
import sys
import os

# Add the parent directory to the Python path so we can import the blog module
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from blog.app import app  # Main API application

async def handle_asgi_request(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    asgi_request = AsgiRequest(req, context)
    scope = asgi_request.to_asgi_http_scope()
    asgi_response = await AsgiResponse.from_app(app, scope, req.get_body())
    return asgi_response.to_func_response()

async def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await handle_asgi_request(req, context)
