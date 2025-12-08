# 🤖 GitHub Actions CI/CD Setup Guide

Complete guide to set up automated testing, building, and deployment with GitHub Actions.

---

## 📋 Overview

The CI/CD pipeline automatically:
1. ✅ Runs code quality checks
2. ✅ Executes unit tests with coverage
3. ✅ Runs integration tests
4. ✅ Scans for security vulnerabilities
5. ✅ Builds Docker image
6. ✅ Deploys to Render (on main branch)
7. ✅ Monitors post-deployment health

---

## 🔐 Step 1: Add GitHub Secrets

In your GitHub repository, add these secrets:

### Navigate to Secrets

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**

### Required Secrets

```bash
# Render Deployment
RENDER_API_KEY=rnd_xxxxxxxxxxxxxxxxxxxxx
RENDER_SERVICE_ID=srv-xxxxxxxxxxxxx
RENDER_SERVICE_URL=https://your-service.onrender.com

# Database (for testing)
DATABASE_URL=postgresql://user:pass@neon.tech/test_db

# Docker Hub (optional)
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_token_or_password
```

### How to Get Each Secret

#### RENDER_API_KEY
1. Go to https://dashboard.render.com
2. Click your profile → **Account Settings**
3. Go to **API Keys** tab
4. Click **Create API Key**
5. Copy the key (starts with `rnd_`)

#### RENDER_SERVICE_ID
From your service URL:
```
https://dashboard.render.com/web/srv-xxxxxxxxxxxxx
                                    ↑ This is your SERVICE_ID
```

Or from service settings:
1. Go to your service
2. Look at browser URL
3. Copy the `srv-xxxxxxxxxxxxx` part

#### RENDER_SERVICE_URL
Your public service URL:
```
https://your-service-name.onrender.com
```

#### DATABASE_URL
Your Neon PostgreSQL connection string:
```
postgresql://username:password@ep-xxx.region.aws.neon.tech/mldb?sslmode=require
```

---

## 📝 Step 2: Workflow File

The workflow file is already created at `.github/workflows/ci-cd.yml`.

### Workflow Triggers

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
```

**Triggers:**
- Push to `main` or `develop` branch
- Pull request targeting `main`

---

## 🔍 Step 3: Understanding Pipeline Jobs

### Job 1: Code Quality (`lint`)

**What it does:**
- Checks code formatting with Black
- Lints code with Flake8
- Verifies import sorting with isort

**Duration:** ~2-3 minutes

**Fails if:**
- Code not formatted with Black
- Linting errors found
- Imports not sorted

### Job 2: Unit Tests (`test`)

**What it does:**
- Sets up PostgreSQL test database
- Installs dependencies
- Runs pytest with coverage
- Uploads coverage to Codecov

**Duration:** ~3-5 minutes

**Fails if:**
- Any test fails
- Coverage below threshold

### Job 3: Integration Tests (`integration-test`)

**What it does:**
- Starts PostgreSQL database
- Sets up Prisma
- Starts FastAPI server
- Tests API endpoints

**Duration:** ~3-5 minutes

**Fails if:**
- API endpoints don't respond
- Integration tests fail

### Job 4: Security Scan (`security`)

**What it does:**
- Scans code with Trivy
- Checks for vulnerabilities
- Uploads results to GitHub Security

**Duration:** ~2-3 minutes

**Fails if:**
- Critical vulnerabilities found

### Job 5: Build Docker (`build`)

**What it does:**
- Builds Docker image
- Tests container startup
- Pushes to Docker Hub (main branch only)

**Duration:** ~5-8 minutes

**Fails if:**
- Docker build fails
- Container health check fails

### Job 6: Deploy to Render (`deploy`)

**What it does:**
- Triggers Render deployment
- Waits for deployment
- Runs smoke tests

**Duration:** ~3-5 minutes

**Only runs on:** `main` branch

**Fails if:**
- Deployment fails
- Health check fails

### Job 7: Post-Deploy Monitoring (`monitor`)

**What it does:**
- Checks metrics endpoint
- Verifies service health
- Sends deployment notification

**Duration:** ~1-2 minutes

**Only runs on:** `main` branch after deploy

---

## 🚀 Step 4: Triggering the Pipeline

### Automatic Triggers

**On every push to main/develop:**
```bash
git push origin main
```

**On pull request:**
```bash
git checkout -b feature/new-feature
# Make changes
git push origin feature/new-feature
# Create pull request on GitHub
```

### Manual Trigger

1. Go to **Actions** tab in GitHub
2. Select workflow: "ML Backend CI/CD Pipeline"
3. Click **Run workflow**
4. Select branch
5. Click **Run workflow** button

---

## 📊 Step 5: Monitoring Pipeline

### View Pipeline Status

1. Go to **Actions** tab in repository
2. Click on latest workflow run
3. View job status and logs

### Status Badges

Add to README.md:
```markdown
![CI/CD](https://github.com/your-username/your-repo/actions/workflows/ci-cd.yml/badge.svg)
```

### Email Notifications

GitHub automatically sends emails on:
- Workflow failures
- First-time contributor PRs

### Slack Notifications (Optional)

Add to workflow:
```yaml
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🐛 Step 6: Troubleshooting

### Pipeline Failing at Lint Stage

**Error:** "Files would be reformatted by Black"

**Solution:**
```bash
# Format code locally
black app/

# Sort imports
isort app/

# Commit and push
git add .
git commit -m "Format code"
git push
```

### Pipeline Failing at Test Stage

**Error:** "Database connection failed"

**Solution:**
1. Check `DATABASE_URL` secret is set
2. Verify PostgreSQL service is running
3. Check test database exists

```bash
# Test locally
pytest tests/ --verbose
```

### Pipeline Failing at Build Stage

**Error:** "Docker build failed"

**Solution:**
```bash
# Test Docker build locally
cd ml-backend
docker build -t test-build .

# Check Dockerfile syntax
# Check all dependencies in requirements.txt
```

### Pipeline Failing at Deploy Stage

**Error:** "Render API error"

**Solution:**
1. Verify `RENDER_API_KEY` is correct
2. Check `RENDER_SERVICE_ID` is correct
3. Ensure service exists on Render

```bash
# Test Render API
curl -H "Authorization: Bearer $RENDER_API_KEY" \
  "https://api.render.com/v1/services/$RENDER_SERVICE_ID"
```

### Pipeline Slow

**Solutions:**
1. **Enable caching:**
   ```yaml
   - name: Cache Python dependencies
     uses: actions/cache@v3
     with:
       path: ~/.cache/pip
       key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
   ```

2. **Parallelize jobs:**
   - Jobs without dependencies run in parallel
   - Already configured in current workflow

3. **Use GitHub-hosted runners:**
   - Already using: `ubuntu-latest`
   - Fast and reliable

---

## 🔒 Step 7: Security Best Practices

### 1. Protect Secrets

- Never commit secrets to repository
- Use GitHub Secrets for sensitive data
- Rotate secrets regularly

### 2. Branch Protection

Enable branch protection for `main`:
1. Go to **Settings** → **Branches**
2. Add rule for `main` branch
3. Enable:
   - Require status checks (all CI jobs must pass)
   - Require pull request reviews
   - Require signed commits

### 3. Code Scanning

Enable GitHub Advanced Security:
1. Go to **Settings** → **Code security**
2. Enable Dependabot alerts
3. Enable Code scanning

### 4. Audit Logs

Monitor Actions usage:
1. Go to **Settings** → **Actions** → **Usage**
2. View workflow runs
3. Check for unusual activity

---

## 📈 Step 8: Optimizations

### 1. Dependency Caching

Already implemented:
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### 2. Docker Layer Caching

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2
  with:
    driver-opts: |
      image=moby/buildkit:latest
      cache-from=type=gha
      cache-to=type=gha,mode=max
```

### 3. Parallel Matrix Testing

Test multiple Python versions:
```yaml
test:
  strategy:
    matrix:
      python-version: ['3.10', '3.11', '3.12']
  steps:
    - uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
```

### 4. Conditional Jobs

Skip jobs on draft PRs:
```yaml
deploy:
  if: github.ref == 'refs/heads/main' && github.event.pull_request.draft == false
```

---

## 📊 Step 9: Monitoring & Reporting

### Test Coverage

View coverage reports:
1. Pipeline uploads to Codecov
2. View at: https://codecov.io/gh/your-username/your-repo
3. Add badge to README

### Build Times

Track build performance:
1. Go to **Actions** → **Workflow runs**
2. View duration trends
3. Identify slow jobs

### Success Rate

Monitor pipeline health:
1. View success/failure rate
2. Identify flaky tests
3. Fix reliability issues

---

## 🔄 Step 10: Advanced Workflows

### Separate Staging and Production

Create multiple workflows:

**`.github/workflows/staging.yml`**
```yaml
on:
  push:
    branches: [ develop ]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Staging
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_STAGING_API_KEY }}
          RENDER_SERVICE_ID: ${{ secrets.RENDER_STAGING_SERVICE_ID }}
        run: |
          curl -X POST "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY"
```

### Scheduled Runs

Run tests nightly:
```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
```

### Dependency Updates

Auto-update dependencies with Dependabot:

**`.github/dependabot.yml`**
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/ml-backend"
    schedule:
      interval: "weekly"
```

---

## ✅ Setup Checklist

- [ ] Added all GitHub secrets
- [ ] Workflow file exists at `.github/workflows/ci-cd.yml`
- [ ] Branch protection enabled for `main`
- [ ] Tested pipeline on feature branch
- [ ] Verified all jobs pass
- [ ] Deployment to Render successful
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Status badge added to README
- [ ] Team notified of CI/CD setup

---

## 🎉 Your CI/CD Pipeline is Ready!

Every push to `main` now automatically:
1. ✅ Tests your code
2. ✅ Builds Docker image
3. ✅ Deploys to Render
4. ✅ Monitors health

**View pipeline:** https://github.com/your-username/your-repo/actions

---

## 🔗 Resources

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Workflow Syntax**: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
- **Render API Docs**: https://api-docs.render.com
- **Docker Actions**: https://github.com/docker/build-push-action

---

For questions:
- GitHub Community: https://github.community
- Render Community: https://community.render.com
