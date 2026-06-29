"""
Vercel Entry Point - Production Backend with Supabase Integration
"""

import sys
import os

# Add backend directory to path to import app modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Import the main application
from app.api.server import app as fastapi_app

# Ensure CORS is properly configured
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel serverless function handler
def handler(event, context):
    """
    Vercel serverless function handler that wraps FastAPI app
    """
    from mangum import Mangum
    asgi_handler = Mangum(fastapi_app)
    return asgi_handler(event, context)
