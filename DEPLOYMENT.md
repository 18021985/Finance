# Netlify Deployment Guide

This project has been restructured to deploy both frontend (Next.js) and backend (Python) on Netlify using Netlify Functions.

## Architecture

- **Frontend**: Next.js app in `frontend/` directory
- **Backend**: Python serverless functions in `netlify/functions/` directory
- **Database**: Supabase (external service)
- **API Routes**: All `/api/*` requests are routed to Netlify Functions

## Prerequisites

1. Netlify account (free tier available)
2. GitHub account
3. Supabase account (free tier available)
4. Node.js 18+ installed locally

## Deployment Steps

### 1. Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial commit for Netlify deployment"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Set Up Supabase

1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Get your Supabase URL and anon key from Project Settings > API
3. Create necessary tables in Supabase (if using database features)

### 3. Deploy to Netlify

#### Option A: Via Netlify Dashboard

1. Go to [app.netlify.com](https://app.netlify.com)
2. Click "Add new site" > "Import an existing project"
3. Connect your GitHub repository
4. Configure build settings:
   - **Build command**: `cd frontend && npm run build`
   - **Publish directory**: `frontend/.next`
   - **Base directory**: (leave empty)
5. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anon key
   - `PYTHON_VERSION`: `3.9`
6. Click "Deploy site"

#### Option B: Via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize
netlify init

# Deploy
netlify deploy --prod
```

### 4. Configure Environment Variables

In Netlify Dashboard > Site Settings > Build Environment Variables:

```
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
PYTHON_VERSION=3.11
NODE_VERSION=18
```

### 5. Verify Deployment

1. Check the deploy logs in Netlify Dashboard
2. Test the site URL
3. Test API endpoints:
   - `/api/health` - Health check
   - `/api/macro-intelligence` - Macro data
   - `/api/indian-market` - Indian market data

## Important Notes

### Netlify Functions Limitations

- **Execution Time**: 10-60 seconds depending on plan
- **Cold Starts**: Functions may have initial delay on first request
- **Memory**: Limited to 1024MB on free tier
- **Background Tasks**: Not supported - long-running tasks will timeout

### Adjustments Made for Serverless

1. **Removed FastAPI/uvicorn** - Not needed for serverless functions
2. **Removed async/await** - Netlify Functions use synchronous handlers
3. **Simplified routing** - Single `api.py` function handles all routes
4. **CORS handling** - Added CORS headers in response helpers

### Development vs Production

- **Local Development**: Uses `http://localhost:8000` for API
- **Production**: Uses `/api` which routes to Netlify Functions

To test locally with Netlify Functions:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Run local development server
netlify dev
```

## Troubleshooting

### Function Timeout

If functions timeout:
- Reduce data processing complexity
- Implement caching
- Consider upgrading to paid Netlify plan

### Import Errors

If you get import errors:
- Ensure all Python files are in the correct directory structure
- Check that `requirements.txt` includes all dependencies
- Verify the `shared.py` module can import analyzers correctly

### Build Failures

If the build fails:
- Check Netlify build logs
- Ensure Node.js and Python versions are set correctly
- Verify all dependencies are in `package.json` and `requirements.txt`

## Database Setup (Supabase)

If using Supabase for data persistence:

1. Create tables in Supabase SQL editor:
   ```sql
   -- Example table for auto-learning logs
   CREATE TABLE auto_learning_logs (
     id SERIAL PRIMARY KEY,
     timestamp TIMESTAMP DEFAULT NOW(),
     model_name TEXT,
     accuracy_score FLOAT,
     feature_importance JSONB
   );
   ```

2. Set up Row Level Security (RLS) policies as needed

3. Update environment variables with Supabase credentials

## Monitoring

- **Netlify Dashboard**: View function logs, build logs, and site analytics
- **Supabase Dashboard**: Monitor database performance and queries
- **Error Tracking**: Consider adding Sentry or similar for error tracking

## Cost

- **Netlify Free Tier**: $5/month credit (sufficient for small projects)
- **Supabase Free Tier**: 500MB database, 1GB bandwidth/month
- **Total**: Free for development and small-scale production

## Scaling

If you need to scale beyond free tier limits:
- Upgrade Netlify plan for more function execution time
- Upgrade Supabase plan for more database storage
- Consider dedicated backend server for heavy compute tasks
