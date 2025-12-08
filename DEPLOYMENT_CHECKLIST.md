# ✅ Deployment Checklist

Use this checklist to ensure proper deployment setup.

---

## 📋 Pre-Deployment

### Database Setup
- [ ] Neon project created
- [ ] Database connection string obtained
- [ ] Prisma schema generated locally
- [ ] Database schema pushed (`prisma db push`)
- [ ] Connection tested with Prisma Studio

### GitHub Repository
- [ ] Repository created and code pushed
- [ ] All workflow files in `.github/workflows/`
- [ ] Dockerfile.frontend in root directory
- [ ] docker compose
.fullstack.yml in root
- [ ] render.yaml in root directory

### GitHub Secrets
- [ ] `NEON_DATABASE_URL` configured
- [ ] `RENDER_API_KEY` configured
- [ ] `DOCKER_USERNAME` configured (optional)
- [ ] `DOCKER_PASSWORD` configured (optional)

---

## 🚀 Deployment Setup

### Render Services
- [ ] Backend service created
- [ ] Backend DATABASE_URL environment variable set
- [ ] Backend service is healthy
- [ ] Backend URL copied for secrets

- [ ] Frontend service created
- [ ] Frontend NEXT_PUBLIC_API_URL set to backend URL
- [ ] Frontend service is healthy
- [ ] Frontend URL copied for secrets

- [ ] Drift monitor worker created
- [ ] Drift worker DATABASE_URL set
- [ ] Drift worker is running

### Update GitHub Secrets (Post-Render)
- [ ] `RENDER_BACKEND_SERVICE_ID` added
- [ ] `RENDER_FRONTEND_SERVICE_ID` added
- [ ] `RENDER_BACKEND_URL` added
- [ ] `RENDER_FRONTEND_URL` added
- [ ] `NEXT_PUBLIC_API_URL` added (same as backend URL)

---

## 🧪 Testing

### Backend Testing
- [ ] Health endpoint: `/health` returns 200
- [ ] Root endpoint: `/` returns service info
- [ ] API docs: `/docs` loads correctly
- [ ] Metrics endpoint: `/metrics` returns Prometheus metrics
- [ ] Database connection working (check logs)

### Frontend Testing
- [ ] Homepage loads
- [ ] Dashboard page loads: `/dashboard`
- [ ] Health endpoint: `/api/health` returns 200
- [ ] Backend connection works (check Network tab)

### Integration Testing
- [ ] Upload CSV file in dashboard
- [ ] EDA tab shows uploaded data
- [ ] API calls to backend successful
- [ ] No CORS errors in console

---

## 📊 Monitoring Setup

### Prometheus
- [ ] Prometheus accessible (local: `localhost:9090`)
- [ ] Backend metrics being scraped
- [ ] Alert rules loaded
- [ ] Targets are UP

### Grafana
- [ ] Grafana accessible (local: `localhost:3001`)
- [ ] Prometheus data source added
- [ ] Dashboard imported
- [ ] Panels showing data

### MLflow
- [ ] MLflow UI accessible (local: `localhost:5000`)
- [ ] Experiments directory mounted
- [ ] Can create new experiments

---

## 🔄 CI/CD Verification

### GitHub Actions
- [ ] Frontend pipeline passes
- [ ] Backend pipeline passes
- [ ] Full stack pipeline passes
- [ ] Drift monitoring workflow configured

### Pipeline Stages (Backend)
- [ ] Lint stage passes
- [ ] Unit tests pass (with Neon DB)
- [ ] Integration tests pass
- [ ] Security scan completes
- [ ] Docker build succeeds
- [ ] Model validation runs
- [ ] Deployment to Render succeeds
- [ ] Post-deploy monitoring runs

### Pipeline Stages (Frontend)
- [ ] Lint & type check passes
- [ ] Build completes
- [ ] Docker build succeeds
- [ ] Deployment to Render succeeds

---

## 🔐 Security

### Environment Variables
- [ ] No secrets committed to git
- [ ] All secrets in GitHub Secrets
- [ ] All secrets in Render environment variables
- [ ] `.env` files in `.gitignore`

### Docker Security
- [ ] Docker images scanned with Trivy
- [ ] No critical vulnerabilities
- [ ] Non-root user in containers
- [ ] Health checks configured

### Database Security
- [ ] SSL mode required (`?sslmode=require`)
- [ ] Connection pooling enabled
- [ ] No hardcoded credentials

---

## 📈 Performance

### Backend Performance
- [ ] Response time < 500ms for predictions
- [ ] Health check response < 100ms
- [ ] Memory usage < 1GB
- [ ] CPU usage < 70%

### Frontend Performance
- [ ] Page load time < 2 seconds
- [ ] Lighthouse score > 80
- [ ] No console errors
- [ ] Images optimized

---

## 🔔 Alerts & Notifications

### Alert Configuration
- [ ] Alert rules defined in Prometheus
- [ ] Thresholds configured correctly
- [ ] Alert severity levels set

### Notification Channels (Optional)
- [ ] Slack webhook configured
- [ ] Email notifications set up
- [ ] PagerDuty integration (if needed)

---

## 📝 Documentation

### Project Documentation
- [ ] README.md updated with deployment info
- [ ] COMPLETE_CICD_GUIDE.md reviewed
- [ ] QUICKSTART.md followed
- [ ] API documentation accessible

### Team Documentation
- [ ] Deployment process documented
- [ ] Rollback procedure documented
- [ ] Incident response plan created
- [ ] On-call rotation defined (if applicable)

---

## 🎯 Post-Deployment

### Immediate (0-24 hours)
- [ ] Monitor error rates
- [ ] Check response times
- [ ] Verify all endpoints working
- [ ] Test critical user flows
- [ ] Monitor resource usage

### Short-term (1-7 days)
- [ ] Review drift detection reports
- [ ] Check model performance metrics
- [ ] Analyze user feedback
- [ ] Optimize slow endpoints
- [ ] Review logs for errors

### Long-term (1+ months)
- [ ] Review and update alert thresholds
- [ ] Optimize database queries
- [ ] Implement A/B testing
- [ ] Add feature flags
- [ ] Plan for scaling

---

## 🔄 Maintenance Schedule

### Daily
- [ ] Check service health
- [ ] Review error logs
- [ ] Monitor drift scores

### Weekly
- [ ] Review performance metrics
- [ ] Update dependencies (security patches)
- [ ] Review and close incidents

### Monthly
- [ ] Review and update documentation
- [ ] Evaluate resource usage and costs
- [ ] Plan infrastructure improvements
- [ ] Review and improve CI/CD pipeline

---

## 🆘 Emergency Contacts

| Role | Contact | Responsibilities |
|------|---------|------------------|
| DevOps Lead | [Your Name] | CI/CD, infrastructure |
| ML Engineer | [Name] | Model performance, drift |
| Backend Dev | [Name] | API issues, database |
| Frontend Dev | [Name] | UI issues |

---

## 📞 Support Resources

- **Render Status**: https://status.render.com
- **Neon Status**: https://neon.tech/status
- **GitHub Status**: https://www.githubstatus.com
- **Documentation**: See COMPLETE_CICD_GUIDE.md

---

**Last Updated**: December 2025  
**Status**: ✅ Ready for Production  

**Deployment Time**: ~30 minutes  
**First Deploy Date**: ___________  
**Last Deploy Date**: ___________  

🎉 **Congratulations on your production deployment!**
