# 🗄️ Neon PostgreSQL + Prisma Setup Guide

Complete guide to set up Neon PostgreSQL database with Prisma ORM for the ML Backend.

---

## 📋 Prerequisites

- Neon account (sign up at https://neon.tech)
- Python 3.11+
- Git

---

## 🚀 Step 1: Create Neon Database

### 1.1 Sign Up for Neon

1. Go to https://neon.tech
2. Sign up with GitHub or email
3. Create a new project: `credit-scoring-ml`

### 1.2 Get Database Connection String

1. In Neon dashboard, go to your project
2. Navigate to **Connection Details**
3. Copy the connection string (looks like):
   ```
   postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/mldb?sslmode=require
   ```

### 1.3 Configure Environment Variable

Create `.env` file in `ml-backend/` directory:

```bash
# ml-backend/.env
DATABASE_URL="postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/mldb?sslmode=require"
```

---

## 🔧 Step 2: Install Dependencies

```bash
cd ml-backend

# Install Python dependencies
pip install -r requirements.txt

# Install Prisma
pip install prisma

# Generate Prisma client
prisma generate
```

---

## 📊 Step 3: Setup Database Schema

### 3.1 Push Schema to Database

```bash
# Push Prisma schema to Neon database
prisma db push
```

This will create all tables defined in `prisma/schema.prisma`:
- ✅ models
- ✅ predictions
- ✅ model_metrics
- ✅ drift_reports
- ✅ experiments
- ✅ experiment_runs
- ✅ alerts
- ✅ api_usage
- ✅ system_health

### 3.2 Verify Schema

```bash
# Open Prisma Studio to view database
prisma studio
```

This opens a GUI at `http://localhost:5555` to browse your database.

---

## 🧪 Step 4: Test Database Connection

Run the setup script:

```bash
python scripts/setup_database.py
```

Expected output:
```
🚀 Starting database setup...
✅ Database connection successful
Testing database operations...
Found 0 models in database
Found 0 unacknowledged alerts
✅ Database operations test passed
✅ Database setup complete!
```

---

## 🌱 Step 5: Seed Sample Data (Optional)

```bash
python scripts/setup_database.py --seed
```

This will create:
- Sample trained model
- Sample prediction
- Test data for development

---

## 🔄 Step 6: Database Migrations

### When You Update Schema

1. Edit `prisma/schema.prisma`
2. Generate new client:
   ```bash
   prisma generate
   ```
3. Push changes:
   ```bash
   prisma db push
   ```

### For Production (Recommended)

Use Prisma Migrate for version-controlled migrations:

```bash
# Create migration
prisma migrate dev --name add_new_feature

# Apply migration to production
prisma migrate deploy
```

---

## 📝 Database Schema Overview

### Models Table
Stores trained model metadata:
- Model name, version, type
- Performance metrics (accuracy, AUC, fairness)
- Hyperparameters
- Feature importance
- Active status

### Predictions Table
Logs all predictions for monitoring:
- Input features
- Prediction results
- Confidence and risk scores
- Latency metrics
- Optional ground truth feedback

### Model Metrics Table
Time-series performance tracking:
- Accuracy, precision, recall, F1, AUC
- Fairness metrics
- Business metrics
- Time period windows

### Drift Reports Table
Drift detection results:
- Drift scores
- Drifted features list
- Performance changes
- Alert levels
- Recommendations

### Alerts Table
System alerts and notifications:
- Drift alerts
- Performance alerts
- System health alerts

### API Usage Table
Track API requests:
- Endpoint, method, status
- Response times
- Error tracking

### System Health Table
System resource monitoring:
- CPU, memory, disk usage
- Active models count
- Prediction volume
- Error rates

---

## 🔍 Querying the Database

### Using Prisma Client (Python)

```python
from app.database import db_manager

# Get active model
model = await db_manager.get_active_model("random_forest")

# Log prediction
await db_manager.log_prediction(
    model_id=model.id,
    features={"credit_score": 750, "income": 75000},
    prediction=1,
    probability=0.84,
    confidence=0.92,
    risk_score=0.16,
    latency=45.5
)

# Get recent predictions
predictions = await db_manager.get_recent_predictions(limit=100)

# Log drift report
await db_manager.log_drift_report(
    model_id=model.id,
    drift_report=drift_data,
    reference_start=start_date,
    reference_end=end_date,
    current_start=curr_start,
    current_end=curr_end,
    reference_size=1000,
    current_size=1000
)
```

### Using Raw SQL

```python
from app.database import get_prisma_client

client = get_prisma_client()
await client.connect()

# Execute raw query
result = await client.query_raw(
    'SELECT COUNT(*) FROM predictions WHERE "modelId" = $1',
    model_id
)
```

---

## 🌐 Database Studio (GUI)

### Local Development

```bash
prisma studio
```

Opens at: http://localhost:5555

### Production (Neon Console)

1. Go to Neon dashboard
2. Click on your database
3. Use SQL Editor for queries

---

## 🔒 Security Best Practices

### 1. Environment Variables

Never commit `.env` file:
```bash
echo ".env" >> .gitignore
```

### 2. Connection Pooling

Neon automatically provides connection pooling. Use the pooled connection string:
```
postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/mldb?sslmode=require&pgbouncer=true
```

### 3. SSL/TLS

Always use `sslmode=require` in production.

### 4. Database Backups

Neon provides automatic backups:
- Point-in-time recovery
- Daily snapshots
- Configurable retention

---

## 📊 Monitoring

### Connection Status

```python
from app.database import get_prisma_client

client = get_prisma_client()
is_connected = client.is_connected()
print(f"Database connected: {is_connected}")
```

### Query Performance

Monitor slow queries in Neon dashboard:
1. Go to **Monitoring** tab
2. View **Query Performance**
3. Identify slow queries

### Database Size

Check database size in Neon dashboard under **Usage**.

---

## 🐛 Troubleshooting

### Error: Cannot connect to database

**Solution:**
1. Verify `DATABASE_URL` in `.env`
2. Check Neon project is active
3. Ensure IP is not blocked (Neon allows all by default)

```bash
# Test connection
python -c "import asyncio; from app.database import connect_database; asyncio.run(connect_database())"
```

### Error: Prisma client not found

**Solution:**
```bash
prisma generate
```

### Error: Table does not exist

**Solution:**
```bash
prisma db push
```

### Migration Conflicts

**Solution:**
```bash
# Reset database (development only!)
prisma migrate reset

# Or manually drop conflicting migrations
prisma migrate resolve --rolled-back <migration_name>
```

---

## 🚀 Production Deployment

### 1. Set Environment Variable on Render

In Render dashboard:
1. Go to your service
2. Navigate to **Environment** tab
3. Add:
   ```
   DATABASE_URL=postgresql://...neon.tech/mldb?sslmode=require
   ```

### 2. Run Migrations on Deploy

Add to `render.yaml`:
```yaml
services:
  - type: web
    buildCommand: |
      pip install -r requirements.txt
      prisma generate
      prisma db push --skip-generate
```

### 3. Health Checks

Render will use `/health` endpoint which checks database connection.

---

## 📈 Scaling

### Read Replicas

Neon supports read replicas for scaling reads:

1. Create read replica in Neon dashboard
2. Get read replica connection string
3. Configure in application:

```python
# Write operations - primary
PRIMARY_DB_URL = "postgresql://...primary..."

# Read operations - replica
REPLICA_DB_URL = "postgresql://...replica..."
```

### Connection Pooling

Use PgBouncer (built into Neon):
```
DATABASE_URL=postgresql://...?pgbouncer=true&connect_timeout=10
```

---

## 🔗 Resources

- **Neon Docs**: https://neon.tech/docs
- **Prisma Docs**: https://www.prisma.io/docs
- **Prisma Python Client**: https://prisma-client-py.readthedocs.io
- **Connection Pooling**: https://neon.tech/docs/connect/connection-pooling

---

## ✅ Checklist

- [ ] Created Neon account and project
- [ ] Copied DATABASE_URL to `.env`
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Generated Prisma client (`prisma generate`)
- [ ] Pushed schema to database (`prisma db push`)
- [ ] Tested database connection (`python scripts/setup_database.py`)
- [ ] Seeded sample data (optional, `--seed` flag)
- [ ] Configured environment variable on Render
- [ ] Verified health check endpoint works

---

**🎉 Your Neon + Prisma database is ready!**

For questions or issues, check:
- Neon Status: https://neon.tech/status
- Community Discord: https://discord.gg/neon
