"""
Vercel Serverless Function Entry Point for FastAPI Backend

This file bridges Vercel's serverless environment with your FastAPI application.

Deployment:
1. Add to vercel.json:
   {
     "builds": [
       { "src": "vercel.py", "use": "@vercel/python" }
     ],
     "routes": [
       { "src": "/(.*)", "dest": "vercel.py" }
     ]
   }

2. Deploy: vercel --prod
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import your FastAPI app
from app.api.server import app

# Vercel handler
handler = app

# For local testing with serverless
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
