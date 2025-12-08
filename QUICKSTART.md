# 🚀 Quick Start Guide - CI/CD Setup

## Prerequisites

- GitHub account with repository access
- [Neon](https://neon.tech) account (free tier available)
- [Render](https://render.com) account (free tier available)
- [Docker Hub](https://hub.docker.com) account (optional)

---

## 1️⃣ Database Setup (5 minutes)

### Create Neon Database

1. Go to [neon.tech](https://neon.tech) → Sign up/Login
2. Click **"New Project"**
3. **Project name**: `credit-scoring-ml`
4. **Region**: Select closest to your users
5. Click **"Create Project"**
6. **Copy the connection string** (looks like):
   ```
   postgresql://user:pass@ep-xxx.region.neon.tech/dbname?sslmode=require
   ```

### Initialize Database

```bash
cd ml-backend

# Create .env file
echo "DATABASE_URL=<your-neon-connection-string>" > .env

# Install Prisma
pip install prisma

# Generate Prisma client
prisma generate

# Push schema to database
prisma db push

# ✅ Verify connection
prisma studio
```

---

## 2️⃣ GitHub Secrets Setup (5 minutes)

Go to: **Your Repo → Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

Add these one by one:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `NEON_DATABASE_URL` | Your Neon connection string | From Neon dashboard (Step 1) |
| `RENDER_API_KEY` | Your Render API key | Render → Account Settings → API Keys |
| `RENDER_BACKEND_SERVICE_ID` | Backend service ID | Create service first (Step 3) |
| `RENDER_FRONTEND_SERVICE_ID` | Frontend service ID | Create service first (Step 3) |
| `RENDER_BACKEND_URL` | Backend URL | After backend deployment |
| `RENDER_FRONTEND_URL` | Frontend URL | After frontend deployment |
| `NEXT_PUBLIC_API_URL` | Backend URL | Same as RENDER_BACKEND_URL |

### Optional Secrets (for Docker Hub)

| Secret Name | Value |
|-------------|-------|
| `DOCKER_USERNAME` | Your Docker Hub username |
| `DOCKER_PASSWORD` | Your Docker Hub password/token |

---

## 3️⃣ Render Deployment (10 minutes)

### Option A: Using render.yaml (Recommended)

1. **Push your code** to GitHub (including render.yaml)
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Render will detect `render.yaml` and create all services automatically
6. Set environment variable: `DATABASE_URL` for all services
7. Click **"Apply"**

### Option B: Manual Setup

#### Create Backend Service

1. **New +** → **Web Service**
2. **Connect Repository**
3. **Settings**:
   - **Name**: `credit-scoring-ml-backend`
   - **Root Directory**: `ml-backend`
   - **Environment**: `Docker`
   - **Region**: Oregon (or closest)
   - **Plan**: Standard ($25/mo) or Starter ($7/mo)
4. **Environment Variables**: Add `DATABASE_URL`
5. **Create Web Service**

#### Create Frontend Service

1. **New +** → **Web Service**
2. **Connect Repository**
3. **Settings**:
   - **Name**: `credit-scoring-frontend`
   - **Root Directory**: Leave empty (root)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile.frontend`
   - **Plan**: Starter ($7/mo)
4. **Environment Variables**: Add `NEXT_PUBLIC_API_URL` (backend URL)
5. **Create Web Service**

#### Create Background Workers

1. **New +** → **Background Worker**
2. **Connect Repository**
3. **Settings**:
   - **Name**: `drift-monitor`
   - **Root Directory**: `ml-backend`
   - **Docker Command**: `python -m app.workers.drift_monitor`
4. Add `DATABASE_URL`
5. **Create**

---

## 4️⃣ Update GitHub Secrets with Render URLs

After services are deployed:

1. Copy **Backend URL** from Render (e.g., `https://credit-scoring-ml-backend.onrender.com`)
2. Copy **Frontend URL** from Render (e.g., `https://credit-scoring-frontend.onrender.com`)
3. Copy **Service IDs** (from service URL: `/services/srv-xxxxx`)

Update these secrets in GitHub:
- `RENDER_BACKEND_URL`
- `RENDER_FRONTEND_URL`
- `RENDER_BACKEND_SERVICE_ID`
- `RENDER_FRONTEND_SERVICE_ID`
- `NEXT_PUBLIC_API_URL`

---

## 5️⃣ Trigger First Deployment

```bash
# Make a small change
echo "\n# CI/CD Setup Complete" >> README.md

# Commit and push
git add .
git commit -m "🚀 Setup CI/CD pipeline"
git push origin main
```

### Watch the Pipeline

1. Go to **GitHub → Actions** tab
2. You'll see 3 workflows running:
   - ✅ Frontend CI/CD Pipeline (~15 min)
   - ✅ Backend CI/CD Pipeline (~25 min)
   - ✅ Full Stack CI/CD (~30 min)

---

## 6️⃣ Verify Deployment

### Check Backend

```bash
# Health check
curl https://your-backend.onrender.com/health

# API docs
curl https://your-backend.onrender.com/docs

# Metrics
curl https://your-backend.onrender.com/metrics
```

### Check Frontend

```bash
# Homepage
curl https://your-frontend.onrender.com

# Health check
curl https://your-frontend.onrender.com/api/health
```

### Test Integration

Open browser:
- **Frontend**: https://your-frontend.onrender.com
- **Dashboard**: https://your-frontend.onrender.com/dashboard
- **API Docs**: https://your-backend.onrender.com/docs

---

## 7️⃣ Local Development Setup

### Backend

```bash
cd ml-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup Prisma
prisma generate

# Run server
uvicorn app.main:app --reload --port 8000
```

**Access**: http://localhost:8000

### Frontend

```bash
# Install dependencies
npm install

# Run dev server
npm run dev
```

**Access**: http://localhost:3000

### Full Stack with Docker

```bash
# Start all services
docker compose
 -f docker compose
.fullstack.yml up -d

# Check logs
docker compose
 -f docker compose
.fullstack.yml logs -f

# Stop services
docker compose
 -f docker compose
.fullstack.yml down
```

**Services**:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- MLflow: http://localhost:5000

---

## 8️⃣ Enable Monitoring

### Prometheus + Grafana (Local)

```bash
# Start monitoring stack
docker compose
 -f docker compose
.fullstack.yml up prometheus grafana -d

# Access Grafana
open http://localhost:3001
# Login: admin / admin
```

### Setup Grafana Dashboard

1. **Add Data Source**: Prometheus (http://prometheus:9090)
2. **Import Dashboard**: Upload `monitoring/grafana/dashboards/ml-system-dashboard.json`
3. **View Metrics**: Real-time system monitoring

---

## 9️⃣ Test CI/CD Pipeline

### Trigger Backend Pipeline

```bash
# Make change in backend
echo "# Updated" >> ml-backend/README.md
git add ml-backend/
git commit -m "test: backend pipeline"
git push
```

### Trigger Frontend Pipeline

```bash
# Make change in frontend
echo "// Updated" >> src/app/page.tsx
git add src/
git commit -m "test: frontend pipeline"
git push
```

### Monitor Pipeline

GitHub → Actions → Watch workflows execute

---

## 🎉 Success Checklist

- [ ] Neon database created and connected
- [ ] GitHub secrets configured (8 secrets)
- [ ] Render services deployed (backend + frontend)
- [ ] CI/CD pipeline passes on GitHub Actions
- [ ] Backend API accessible and healthy
- [ ] Frontend loads and connects to backend
- [ ] Database operations work (via Prisma Studio)
- [ ] Monitoring dashboards accessible
- [ ] Drift detection worker running

---

## 📊 What Happens Now?

### On Every Push to Main:

1. **Automated Tests** run (unit + integration)
2. **Docker Images** built and scanned for security
3. **Model Validation** checks performance thresholds
4. **Deployment** to Render (if tests pass)
5. **Health Checks** verify deployment success
6. **Monitoring** tracks system metrics

### Background Tasks:

- **Drift Detection**: Runs every 6 hours (GitHub Actions) + continuously (Render Worker)
- **Model Retraining**: Daily at 2 AM UTC
- **Health Monitoring**: Every 30 minutes

---

## 🆘 Troubleshooting

### Pipeline Fails

**Check logs**: GitHub → Actions → Failed workflow → View logs

**Common fixes**:
- Verify all GitHub secrets are set correctly
- Check DATABASE_URL includes `?sslmode=require`
- Ensure Render services have environment variables

### Deployment Fails

**Check Render logs**: Render Dashboard → Service → Logs

**Common fixes**:
- Increase plan if OOM errors (Out of Memory)
- Check DATABASE_URL is set in Render
- Verify Dockerfile paths are correct

### Database Connection Issues

```bash
# Test connection
cd ml-backend
python -c "from prisma import Prisma; db = Prisma(); db.connect(); print('✅ Connected')"
```

---

## 📚 Next Steps

1. ✅ Read [COMPLETE_CICD_GUIDE.md](./COMPLETE_CICD_GUIDE.md) for details
2. ✅ Set up Slack/email alerts for drift detection
3. ✅ Configure custom domain names
4. ✅ Add end-to-end tests
5. ✅ Set up log aggregation (Logtail/Papertrail)

---

## 🎯 Support

- **Issues**: GitHub Issues tab
- **Render Docs**: https://render.com/docs
- **Neon Docs**: https://neon.tech/docs
- **Prisma Docs**: https://prisma.io/docs

**Setup Time**: ~25 minutes  
**Status**: ✅ Production Ready  

🚀 **You're now live with full CI/CD!**
