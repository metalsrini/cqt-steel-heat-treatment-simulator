# C-Q-T Steel Heat Treatment Simulator - Deployment Guide

## 🚀 Deploy to Render.com - Complete Setup

This guide will help you deploy the C-Q-T Steel Heat Treatment Simulator to Render.com with both backend API and frontend static site.

## Prerequisites

- GitHub account with your project repository
- Render.com account (free tier available)
- Project fully tested locally

## Deployment Architecture

```
Frontend (Static Site)  →  Backend (Web Service)
      ↓                         ↓
  Render Static Site      Render Web Service
     (React)               (FastAPI + Python)
```

## Step 1: Prepare Your Repository

### 1.1 Repository Structure
Ensure your repository has this structure:
```
zed AI/
├── web_application/
│   ├── backend/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── frontend/
│       ├── package.json
│       ├── .env.production
│       └── build.sh
├── core/
├── render.yaml
└── DEPLOYMENT.md
```

### 1.2 Commit All Changes
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

## Step 2: Deploy Backend to Render

### 2.1 Create Backend Service
1. Log into Render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- Name: `cqt-steel-simulator-backend`
- Environment: `Python 3`
- Region: `Oregon (US West)`
- Branch: `main`
- Root Directory: Leave empty

**Build & Deploy:**
- Build Command: 
  ```bash
  cd web_application/backend && pip install -r requirements.txt
  ```
- Start Command:
  ```bash
  cd web_application/backend && python main.py
  ```

**Environment Variables:**
```
PYTHONPATH=/opt/render/project/src
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info
ALLOWED_ORIGINS=https://your-frontend-app.onrender.com
```

### 2.2 Advanced Settings
- Health Check Path: `/api/health`
- Auto-Deploy: `Yes`

### 2.3 Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Note your backend URL: `https://cqt-steel-simulator-backend.onrender.com`

## Step 3: Deploy Frontend to Render

### 3.1 Create Frontend Service
1. Click "New +" → "Static Site"
2. Connect the same GitHub repository
3. Configure the service:

**Basic Settings:**
- Name: `cqt-steel-simulator-frontend`
- Branch: `main`
- Root Directory: Leave empty

**Build Settings:**
- Build Command:
  ```bash
  cd web_application/frontend && npm ci && npm run build
  ```
- Publish Directory: `web_application/frontend/build`

**Environment Variables:**
```
NODE_ENV=production
REACT_APP_API_URL=https://cqt-steel-simulator-backend.onrender.com
REACT_APP_ENVIRONMENT=production
GENERATE_SOURCEMAP=false
```

### 3.2 Deploy
1. Click "Create Static Site"
2. Wait for deployment (3-5 minutes)
3. Note your frontend URL: `https://cqt-steel-simulator-frontend.onrender.com`

## Step 4: Update CORS Configuration

### 4.1 Update Backend Environment Variables
1. Go to your backend service in Render
2. Click "Environment"
3. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://cqt-steel-simulator-frontend.onrender.com
   ```
4. Click "Save Changes"
5. Service will auto-redeploy

## Step 5: Verification

### 5.1 Test Backend Health
Visit: `https://your-backend-app.onrender.com/api/health`

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-XX...",
  "models_loaded": true
}
```

### 5.2 Test API Endpoints
- Steel Grades: `/api/steel-grades`
- Quench Media: `/api/quench-media`
- Docs: `/api/docs`

### 5.3 Test Frontend Application
1. Visit your frontend URL
2. Verify dropdowns are populated
3. Run a complete simulation
4. Check all features work

## Step 6: Custom Domain (Optional)

### 6.1 Add Custom Domain to Frontend
1. In Render dashboard, go to your frontend service
2. Click "Settings" → "Custom Domains"
3. Add your domain (e.g., `cqt-simulator.yourdomain.com`)
4. Follow DNS configuration instructions

### 6.2 Update Backend CORS
Update backend `ALLOWED_ORIGINS` to include your custom domain:
```
ALLOWED_ORIGINS=https://cqt-simulator.yourdomain.com,https://cqt-steel-simulator-frontend.onrender.com
```

## Environment Variables Reference

### Backend (.env)
```bash
# Server Configuration
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production

# CORS Configuration
ALLOWED_ORIGINS=https://your-frontend-app.onrender.com

# Logging
LOG_LEVEL=info

# Optional Settings
MAX_REQUESTS_PER_MINUTE=100
MAX_SIMULATION_TIME_SECONDS=300
MAX_SPATIAL_POINTS=201
```

### Frontend (.env.production)
```bash
REACT_APP_API_URL=https://your-backend-app.onrender.com
REACT_APP_ENVIRONMENT=production
REACT_APP_APP_NAME=C-Q-T Steel Heat Treatment Simulator
REACT_APP_VERSION=1.0.0
REACT_APP_TIMEOUT=300000
REACT_APP_DEBUG=false
GENERATE_SOURCEMAP=false
```

## Troubleshooting

### Common Issues

**1. Backend Won't Start**
- Check build logs for Python/dependency errors
- Verify `requirements.txt` is complete
- Ensure `PYTHONPATH` is set correctly

**2. Frontend Build Fails**
- Check for Node.js version compatibility
- Verify all npm dependencies are installed
- Check TypeScript compilation errors

**3. CORS Errors**
- Verify `ALLOWED_ORIGINS` includes frontend URL
- Check backend service has redeployed after CORS update
- Ensure URLs match exactly (https vs http)

**4. API Calls Fail**
- Verify `REACT_APP_API_URL` points to correct backend
- Check backend health endpoint
- Review browser network tab for specific errors

**5. Simulation Hangs**
- Check backend logs for errors
- Verify all mathematical models are imported correctly
- Check for missing methods or hardcoded values

### Debugging Steps

1. **Check Service Logs:**
   - In Render dashboard, click service → "Logs"
   - Look for startup errors or runtime exceptions

2. **Verify Environment Variables:**
   - Backend: Go to service → "Environment"
   - Frontend: Check build logs for env var usage

3. **Test API Manually:**
   ```bash
   curl https://your-backend-app.onrender.com/api/health
   ```

4. **Check Network Requests:**
   - Open browser dev tools → Network tab
   - Try simulation and check for failed requests

## Performance Optimization

### Backend Optimizations
- Enable request compression
- Add response caching for steel grades/quench media
- Implement rate limiting
- Use connection pooling

### Frontend Optimizations
- Enable static file caching
- Minimize bundle size
- Use lazy loading for components
- Implement service workers

## Security Considerations

1. **Environment Variables:**
   - Never commit sensitive data to repository
   - Use Render's environment variable system

2. **CORS Configuration:**
   - Only allow specific frontend domains
   - Don't use wildcard (*) in production

3. **API Security:**
   - Implement rate limiting
   - Add request validation
   - Monitor for abuse

## Monitoring & Maintenance

### Health Monitoring
- Set up Render health checks
- Monitor response times
- Track error rates

### Updates & Deployments
- Use feature branches for changes
- Test locally before deploying
- Monitor deployment logs

### Backup Strategy
- Repository is backed up on GitHub
- No persistent data to backup
- Configuration documented in this guide

## Cost Considerations

### Render.com Pricing (as of 2024)
- **Static Sites:** Free for personal projects
- **Web Services:** Free tier available (750 hours/month)
- **Custom Domains:** Free
- **Bandwidth:** Generous free allowances

### Optimization Tips
- Use free tier efficiently
- Monitor resource usage
- Scale only when necessary

## Support & Resources

- **Render Documentation:** https://render.com/docs
- **GitHub Repository Issues:** Use for bug reports
- **Render Community:** https://community.render.com
- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **React Documentation:** https://react.dev

## Success Criteria

Your deployment is successful when:
- ✅ Backend health endpoint returns 200 OK
- ✅ Frontend loads without errors
- ✅ Steel grades dropdown is populated
- ✅ Simulations complete successfully
- ✅ Results display correctly with charts
- ✅ Different steel compositions produce different results
- ✅ All features work end-to-end

## Next Steps

After successful deployment:
1. Share your application URL
2. Gather user feedback
3. Monitor performance metrics
4. Plan feature enhancements
5. Consider adding user authentication
6. Implement advanced analytics

Your C-Q-T Steel Heat Treatment Simulator is now live and accessible worldwide! 🚀