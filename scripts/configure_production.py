#!/usr/bin/env python3
"""
Production Environment Configuration Helper

This script helps configure the dashboard for production deployment
by updating the VITE_API_URL in the dashboard .env file.

Usage:
    python scripts/configure_production.py --backend-url https://api.yourdomain.com
    python scripts/configure_production.py --check
"""

import argparse
import os
import sys
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def load_env_file(env_path: Path) -> dict:
    """Load .env file into a dictionary."""
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


def save_env_file(env_path: Path, env_vars: dict):
    """Save dictionary to .env file."""
    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")


def update_dashboard_config(backend_url: str):
    """Update dashboard .env with production backend URL."""
    project_root = get_project_root()
    dashboard_env = project_root / "dashboard" / ".env"
    
    if not dashboard_env.exists():
        print(f"❌ Dashboard .env not found: {dashboard_env}")
        return False
    
    # Load current config
    env_vars = load_env_file(dashboard_env)
    old_url = env_vars.get("VITE_API_URL", "Not set")
    
    # Update URL
    env_vars["VITE_API_URL"] = backend_url
    
    # Save updated config
    save_env_file(dashboard_env, env_vars)
    
    print(f"✅ Updated dashboard configuration:")
    print(f"   Old URL: {old_url}")
    print(f"   New URL: {backend_url}")
    print(f"   File: {dashboard_env}")
    
    return True


def check_production_config():
    """Check current production configuration."""
    project_root = get_project_root()
    dashboard_env = project_root / "dashboard" / ".env"
    backend_env = project_root / ".env"
    
    print("🔍 Production Configuration Check")
    print("=" * 50)
    
    # Check dashboard config
    if dashboard_env.exists():
        dashboard_vars = load_env_file(dashboard_env)
        print(f"\nDashboard .env:")
        print(f"  VITE_API_URL: {dashboard_vars.get('VITE_API_URL', 'Not set')}")
        
        if "localhost" in dashboard_vars.get("VITE_API_URL", ""):
            print(f"  ⚠️  WARNING: Still using localhost - update for production!")
    else:
        print(f"\n❌ Dashboard .env not found: {dashboard_env}")
    
    # Check backend config
    if backend_env.exists():
        backend_vars = load_env_file(backend_env)
        print(f"\nBackend .env:")
        print(f"  DATABASE_URL: {backend_vars.get('DATABASE_URL', 'Not set')}")
        print(f"  SUPABASE_URL: {backend_vars.get('SUPABASE_URL', 'Not set')}")
        
        # Check for placeholder values
        placeholder_keywords = ["your_", "placeholder", "example"]
        for keyword in placeholder_keywords:
            for key, value in backend_vars.items():
                if keyword in value.lower():
                    print(f"  ⚠️  WARNING: {key} still has placeholder value")
    else:
        print(f"\n❌ Backend .env not found: {backend_env}")
    
    print("\n" + "=" * 50)
    
    # Check if .env is in .gitignore
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        with open(gitignore, 'r') as f:
            if ".env" in f.read():
                print("✅ .env is in .gitignore (credentials protected)")
            else:
                print("⚠️  WARNING: .env is NOT in .gitignore")
    else:
        print("⚠️  WARNING: .gitignore not found")
    
    print("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Configure production environment for Spotify Review Analysis Dashboard"
    )
    
    parser.add_argument(
        "--backend-url",
        "-u",
        type=str,
        help="Production backend URL (e.g., https://api.yourdomain.com)"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current production configuration"
    )
    
    args = parser.parse_args()
    
    if args.check:
        check_production_config()
        sys.exit(0)
    
    if args.backend_url:
        success = update_dashboard_config(args.backend_url)
        sys.exit(0 if success else 1)
    
    # If no arguments, show help
    parser.print_help()
    print("\nExamples:")
    print("  python scripts/configure_production.py --backend-url https://api.mydomain.com")
    print("  python scripts/configure_production.py --check")
    sys.exit(1)


if __name__ == "__main__":
    main()
