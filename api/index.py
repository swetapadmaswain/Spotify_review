"""
Vercel Serverless Function Entry Point
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
project_root = Path(__file__).parent.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

# Import the FastAPI app
try:
    from backend.app.api.server import app as fastapi_app
except ImportError:
    from app.api.server import app as fastapi_app

# Vercel serverless function handler
def handler(event, context):
    """
    Vercel serverless function handler that wraps FastAPI app
    """
    from mangum import Mangum
    asgi_handler = Mangum(fastapi_app)
    return asgi_handler(event, context)

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
