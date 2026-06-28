"""
Vercel Serverless Function Entry Point for FastAPI Backend

This file bridges Vercel's serverless environment with your FastAPI application.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables from Vercel
os.environ.setdefault('API_HOST', '0.0.0.0')
os.environ.setdefault('API_PORT', '8000')

try:
    # Import your FastAPI app
    from app.api.server import app as fastapi_app
    handler = fastapi_app
except Exception as e:
    # Fallback handler for debugging
    def fallback_handler(event, context):
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": f"Error loading app: {str(e)}"
        }
    handler = fallback_handler

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
