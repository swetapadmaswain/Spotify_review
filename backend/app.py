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
from app.api.server import app

# Ensure CORS is properly configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = app
