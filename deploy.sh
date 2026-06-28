#!/bin/bash
# Production Deployment Script for Vercel
# Run this script to deploy backend + dashboard to Vercel

set -e  # Exit on error

echo "🚀 Spotify Review Analysis - Production Deployment"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}⚠️  Vercel CLI not found. Installing...${NC}"
    npm install -g vercel
fi

echo -e "${GREEN}✅ Vercel CLI verified${NC}"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please create .env with the following variables:"
    echo "  - DATABASE_URL"
    echo "  - SUPABASE_URL"
    echo "  - SUPABASE_KEY"
    echo "  - OPENAI_API_KEY"
    exit 1
fi

echo -e "${GREEN}✅ Environment file found${NC}"

# Check if dashboard is built
if [ ! -d "dashboard/dist" ]; then
    echo -e "${YELLOW}⚠️  Dashboard not built. Building now...${NC}"
    cd dashboard
    npm install
    npm run build
    cd ..
fi

echo -e "${GREEN}✅ Dashboard built${NC}"

# Deploy to Vercel
echo ""
echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo -e "${GREEN}==================================================${NC}"

echo ""
echo "📝 Next Steps:"
echo "1. Update dashboard environment variables on Vercel:"
echo "   VITE_API_URL=https://your-app.vercel.app"
echo ""
echo "2. Redeploy dashboard to use new API URL"
echo ""
echo "3. Check dashboard at: https://your-app.vercel.app"
echo ""
