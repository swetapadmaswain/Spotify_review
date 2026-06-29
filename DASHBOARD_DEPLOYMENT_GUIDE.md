# Dashboard Deployment Guide

This guide will help you deploy the Spotify Insights Dashboard to production using Vercel.

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Vercel account (free tier works)
- Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Configure Environment Variables

The dashboard needs to connect to your backend API. Create a `.env` file in the `dashboard` directory:

```bash
cd dashboard
```

Create `.env` file with:
```
VITE_API_URL=http://your-backend-api-url.com
```

Replace `http://your-backend-api-url.com` with your actual backend API URL.

## Step 2: Install Dependencies

```bash
npm install
```

## Step 3: Build the Dashboard Locally (Optional)

To test the build locally:

```bash
npm run build
```

This will create a `dist` folder with the production build.

To preview the production build:
```bash
npm run preview
```

## Step 4: Deploy to Vercel

### Option A: Using Vercel CLI (Recommended)

1. Install Vercel CLI globally:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy from the dashboard directory:
```bash
cd dashboard
vercel
```

4. Follow the prompts:
   - **Set up and deploy?** → Yes
   - **Which scope?** → Select your account
   - **Link to existing project?** → No
   - **What's your project's name?** → spotify-insights-dashboard
   - **In which directory is your code located?** → ./
   - **Want to modify these settings?** → No

5. Vercel will detect the Vite configuration and deploy automatically.

### Option B: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com) and log in
2. Click "Add New Project"
3. Import your Git repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `dashboard`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   - Name: `VITE_API_URL`
   - Value: Your backend API URL
6. Click "Deploy"

## Step 5: Configure Environment Variables in Vercel

After deployment, add the environment variable:

1. Go to your project settings in Vercel
2. Navigate to "Environment Variables"
3. Add:
   - **Key**: `VITE_API_URL`
   - **Value**: Your backend API URL (e.g., `https://your-backend.vercel.app`)
   - **Environments**: Production, Preview, Development

## Step 6: Verify Deployment

1. Vercel will provide a deployment URL (e.g., `https://spotify-insights-dashboard.vercel.app`)
2. Visit the URL to verify the dashboard is working
3. Check that the dashboard can connect to your backend API

## Troubleshooting

### Build Fails

If the build fails, check:
- All dependencies are installed (`npm install`)
- TypeScript errors are resolved
- The `vercel.json` configuration is correct

### API Connection Issues

If the dashboard can't connect to the backend:
- Verify `VITE_API_URL` is set correctly in Vercel environment variables
- Ensure your backend API is accessible from the internet
- Check CORS settings on your backend

### TypeScript Errors

If you see TypeScript errors during build:
```bash
npm run build
```

Fix any errors shown before deploying.

## Production Checklist

- [ ] Backend API is deployed and accessible
- [ ] `VITE_API_URL` environment variable is set in Vercel
- [ ] Dashboard builds successfully locally
- [ ] All TypeScript errors are resolved
- [ ] Environment variables are configured for all environments
- [ ] Dashboard loads correctly in production
- [ ] API calls are working in production

## Next Steps

After deploying the dashboard:
1. Deploy the backend API (see BACKEND_DEPLOYMENT_GUIDE.md)
2. Update the dashboard's `VITE_API_URL` to point to the production backend
3. Redeploy the dashboard with the correct API URL
4. Test the full application end-to-end

## Vercel Configuration

The dashboard uses `vercel.json` for deployment configuration:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "devCommand": "npm run dev"
}
```

This tells Vercel to:
- Use npm to build the project
- Output the build to the `dist` directory
- Detect it as a Vite project
- Use `npm run dev` for development

## Custom Domain (Optional)

To use a custom domain:

1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Configure DNS records as instructed by Vercel
5. Wait for SSL certificate to be issued

## Monitoring

Vercel provides built-in monitoring:
- **Analytics**: View visitor statistics
- **Logs**: Check deployment and runtime logs
- **Performance**: Monitor load times and errors

Access these from your project dashboard in Vercel.
