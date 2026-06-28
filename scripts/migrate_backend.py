#!/usr/bin/env python3
"""
Backend Migration Script

This script helps you move the backend to a separate repository.
It creates the necessary files and structure for a standalone backend repo.
"""

import os
import shutil
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def create_backend_structure(backend_dir: Path):
    """Create backend directory structure."""
    backend_dir.mkdir(parents=True, exist_ok=True)
    
    # Create required directories
    (backend_dir / 'app' / 'api').mkdir(parents=True, exist_ok=True)
    (backend_dir / 'app' / 'connectors').mkdir(exist_ok=True)
    (backend_dir / 'app' / 'database').mkdir(exist_ok=True)
    (backend_dir / 'app' / 'models').mkdir(exist_ok=True)
    (backend_dir / 'app' / 'services').mkdir(exist_ok=True)
    (backend_dir / 'config').mkdir(exist_ok=True)


def copy_backend_files(project_root: Path, backend_dir: Path):
    """Copy backend files to new directory."""
    
    # Copy app directory
    app_src = project_root / 'app'
    app_dst = backend_dir / 'app'
    if app_src.exists():
        shutil.copytree(app_src, app_dst, dirs_exist_ok=True)
    
    # Copy config directory
    config_src = project_root / 'config'
    config_dst = backend_dir / 'config'
    if config_src.exists():
        shutil.copytree(config_src, config_dst, dirs_exist_ok=True)
    
    # Copy vercel.py
    vercel_src = project_root / 'vercel.py'
    vercel_dst = backend_dir / 'vercel.py'
    if vercel_src.exists():
        shutil.copy2(vercel_src, vercel_dst)
    
    # Copy vercel.json
    vercel_json_src = project_root / 'vercel.json'
    vercel_json_dst = backend_dir / 'vercel.json'
    if vercel_json_src.exists():
        shutil.copy2(vercel_json_src, vercel_json_dst)
    
    # Copy vercel-build.sh
    build_script_src = project_root / 'vercel-build.sh'
    build_script_dst = backend_dir / 'vercel-build.sh'
    if build_script_src.exists():
        shutil.copy2(build_script_src, build_script_dst)
    
    # Copy requirements.txt
    requirements_src = project_root / 'requirements.txt'
    requirements_dst = backend_dir / 'requirements.txt'
    if requirements_src.exists():
        shutil.copy2(requirements_src, requirements_dst)


def create_backend_vercel_json(backend_dir: Path):
    """Create backend-specific vercel.json."""
    vercel_json = {
        "version": 2,
        "builds": [
            {
                "src": "vercel.py",
                "use": "@vercel/python"
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "vercel.py"
            }
        ]
    }
    
    import json
    vercel_path = backend_dir / 'vercel.json'
    with open(vercel_path, 'w') as f:
        json.dump(vercel_json, f, indent=2)
    
    print(f"✅ Created {vercel_path}")


def create_backend_requirements(backend_dir: Path):
    """Create backend-specific requirements.txt."""
    requirements = """# Core dependencies for data collection
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
google-play-scraper==1.2.7

# Cloud Deployment
supabase==2.5.0

# Utilities
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Logging
loguru==0.7.2

# FastAPI and Server
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0

# LLM Integration
openai==1.3.5
"""
    
    requirements_path = backend_dir / 'requirements.txt'
    with open(requirements_path, 'w') as f:
        f.write(requirements)
    
    print(f"✅ Created {requirements_path}")


def create_backend_readme(backend_dir: Path):
    """Create backend README.md."""
    readme = """# Spotify Review Analysis Backend

FastAPI backend for Spotify Review Discovery Engine.

## Features

- Review data collection (App Store, Play Store, Reddit, Social Media)
- Sentiment analysis
- Pattern detection
- User segmentation
- Root cause analysis
- Unmet needs identification
- AI-powered recommendations

## Environment Variables

| Variable | Description |
|----------|-------------|
| DATABASE_URL | Supabase PostgreSQL connection |
| SUPABASE_URL | Supabase project URL |
| SUPABASE_KEY | Supabase service role key |
| OPENAI_API_KEY | OpenAI API key for LLM analysis |

## Deployment

### Vercel

1. Connect this repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy

### Local Development

```bash
pip install -r requirements.txt
python app/api/server.py
```

## API Endpoints

- `GET /health` - Health check
- `GET /api/insights/summary` - Summary insights
- `GET /api/insights/patterns` - Detected patterns
- `GET /api/insights/segments` - User segments
- `GET /api/insights/root-causes` - Root cause analyses
- `GET /api/insights/unmet-needs` - Unmet needs
- `GET /api/recommendations` - AI recommendations
- `GET /api/roadmap` - Product roadmap

## License

MIT
"""
    
    readme_path = backend_dir / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(readme)
    
    print(f"✅ Created {readme_path}")


def create_gitignore(backend_dir: Path):
    """Create backend .gitignore."""
    gitignore = """# Environment & secrets
.env
.env.local
*.pem

# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/
.pytest_cache/

# Data & generated outputs
vector_db/
reports/
*.log

# IDE & OS
.idea/
.vscode/
.DS_Store
Thumbs.db
"""
    
    gitignore_path = backend_dir / '.gitignore'
    with open(gitignore_path, 'w') as f:
        f.write(gitignore)
    
    print(f"✅ Created {gitignore_path}")


def main():
    """Main function."""
    project_root = get_project_root()
    backend_dir = project_root / 'backend'
    
    print("🚀 Backend Migration Script")
    print("=" * 50)
    print(f"Project root: {project_root}")
    print(f"Backend directory: {backend_dir}")
    print()
    
    # Create backend structure
    print("📁 Creating backend structure...")
    create_backend_structure(backend_dir)
    
    # Copy files
    print("📂 Copying backend files...")
    copy_backend_files(project_root, backend_dir)
    
    # Create backend-specific files
    print("🔧 Creating backend-specific files...")
    create_backend_vercel_json(backend_dir)
    create_backend_requirements(backend_dir)
    create_backend_readme(backend_dir)
    create_gitignore(backend_dir)
    
    print()
    print("=" * 50)
    print("✅ Backend migration preparation complete!")
    print()
    print("Next steps:")
    print("1. Create a new GitHub repository: spotify-backend")
    print("2. Copy contents of 'backend/' folder to new repo")
    print("3. Deploy to Vercel")
    print("4. Update dashboard .env with backend URL")
    print()


if __name__ == "__main__":
    main()
