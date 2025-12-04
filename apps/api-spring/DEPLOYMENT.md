# Deployment Guide - Spring Boot Todo App

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Production Deployment with Docker](#production-deployment-with-docker)
4. [Kubernetes Deployment](#kubernetes-deployment-optional)
5. [Environment Configuration](#environment-configuration)
6. [Database Migrations](#database-migrations)
7. [Monitoring & Observability](#monitoring--observability)
8. [Security Checklist](#security-checklist)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required

- **Java 21** (JDK 21+)
- **Docker** and **Docker Compose** v2.0+
- **PostgreSQL 16** (if not using Docker)
- **Gradle 8.x** (or use wrapper)

### Optional

- **kubectl** for Kubernetes deployments
- **Prometheus** and **Grafana** for monitoring
- **nginx** or **traefik** for reverse proxy

## Local Development

### Quick Start

```bash
cd apps/api-spring

# 1. Start PostgreSQL
docker-compose up -d

# 2. Run migrations
./gradlew flywayMigrate

# 3. Generate jOOQ code
./gradlew generateJooq

# 4. Run tests
./gradlew test

# 5. Start application
./gradlew bootRun
```

The API will be available at `http://localhost:9000`

### Seed Demo Data

```bash
./gradlew seedDatabase
```

**Demo credentials:**
- Guest: `guest1@domain.com` / `Todo####`
- Admin: `admin1@domain.com` / `Todo####`
- Sysadmin: `sysadmin1@domain.com` / `Todo####`

## Production Deployment with Docker

### 1. Prepare Environment

```bash
# Copy production environment template
cp .env.prod.example .env.prod

# Edit .env.prod with your values
nano .env.prod
```

**Critical: Update these values in `.env.prod`:**

- `POSTGRES_PASSWORD` - Strong database password
- `JWT_ACCESS_SECRET` - Random 256-bit secret (generate with `openssl rand -base64 64`)
- `JWT_REFRESH_SECRET` - Different 256-bit secret
- `SENDGRID_API_KEY` - Your SendGrid API key
- `EMAIL_FROM` - Your verified sender email
- `CORS_ALLOWED_ORIGINS` - Your frontend domain(s)

### 2. Build Docker Image

```bash
# Build the application image
docker build -t todo-app-spring:latest .

# Verify image size (should be ~200MB)
docker images todo-app-spring
```

### 3. Deploy with Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check service health
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f app
```

### 4. Run Database Migrations

```bash
# Option A: Run migrations in container
docker-compose -f docker-compose.prod.yml exec app \
  sh -c './gradlew flywayMigrate'

# Option B: Run migrations locally
SPRING_DATABASE_URL=jdbc:postgresql://localhost:5434/todo_spring_prod \
SPRING_DATABASE_USER=todo_user \
SPRING_DATABASE_PASSWORD=your_password \
./gradlew flywayMigrate
```

### 5. Verify Deployment

```bash
# Health check
curl http://localhost:9000/health

# Readiness check
curl http://localhost:9000/readiness

# API documentation
open http://localhost:9000/swagger-ui.html
```

### 6. Optional: Enable Monitoring

```bash
# Start with Prometheus and Grafana
docker-compose -f docker-compose.prod.yml --profile monitoring up -d

# Access Grafana
open http://localhost:3001
# Default credentials: admin / admin (change immediately)
```

## Kubernetes Deployment (Optional)

### Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- Helm 3.x (optional, recommended)

### Basic Kubernetes Manifests

Create `k8s/deployment.yml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-app-secrets
type: Opaque
stringData:
  postgres-password: YOUR_PASSWORD
  jwt-access-secret: YOUR_JWT_ACCESS_SECRET
  jwt-refresh-secret: YOUR_JWT_REFRESH_SECRET
  sendgrid-api-key: YOUR_SENDGRID_KEY

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-app-config
data:
  SPRING_PROFILES_ACTIVE: "prod"
  POSTGRES_DB: "todo_spring_prod"
  POSTGRES_USER: "todo_user"
  EMAIL_FROM: "noreply@yourdomain.com"
  CORS_ALLOWED_ORIGINS: "https://yourdomain.com"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-app-spring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-app-spring
  template:
    metadata:
      labels:
        app: todo-app-spring
    spec:
      containers:
      - name: app
        image: todo-app-spring:latest
        ports:
        - containerPort: 9000
        envFrom:
        - configMapRef:
            name: todo-app-config
        env:
        - name: SPRING_DATABASE_URL
          value: "jdbc:postgresql://postgres-service:5432/todo_spring_prod"
        - name: SPRING_DATABASE_USER
          valueFrom:
            secretKeyRef:
              name: todo-app-secrets
              key: postgres-user
        - name: SPRING_DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: todo-app-secrets
              key: postgres-password
        - name: JWT_ACCESS_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-app-secrets
              key: jwt-access-secret
        - name: JWT_REFRESH_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-app-secrets
              key: jwt-refresh-secret
        - name: SENDGRID_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-app-secrets
              key: sendgrid-api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 9000
          initialDelaySeconds: 40
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /readiness
            port: 9000
          initialDelaySeconds: 20
          periodSeconds: 10
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"

---
apiVersion: v1
kind: Service
metadata:
  name: todo-app-service
spec:
  selector:
    app: todo-app-spring
  ports:
  - port: 80
    targetPort: 9000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace todo-app

# Apply manifests
kubectl apply -f k8s/ -n todo-app

# Check deployment
kubectl get pods -n todo-app
kubectl logs -f deployment/todo-app-spring -n todo-app

# Get service URL
kubectl get svc todo-app-service -n todo-app
```

## Environment Configuration

### Development (.env)

```bash
SPRING_DATABASE_URL=jdbc:postgresql://localhost:5434/todo_spring_dev
SPRING_DATABASE_USER=todo_user
SPRING_DATABASE_PASSWORD=todo_password_dev
SPRING_PORT=9000
SPRING_PROFILES_ACTIVE=dev
JWT_ACCESS_SECRET=dev-access-secret-min-256-bits
JWT_REFRESH_SECRET=dev-refresh-secret-min-256-bits
```

### Production (.env.prod)

See `.env.prod.example` for template.

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SPRING_DATABASE_URL` | Yes | - | PostgreSQL JDBC URL |
| `SPRING_DATABASE_USER` | Yes | - | Database username |
| `SPRING_DATABASE_PASSWORD` | Yes | - | Database password |
| `SPRING_PORT` | No | 9000 | Application port |
| `SPRING_PROFILES_ACTIVE` | No | dev | Profile (dev/prod/test) |
| `JWT_ACCESS_SECRET` | Yes | - | JWT access token secret (256+ bits) |
| `JWT_REFRESH_SECRET` | Yes | - | JWT refresh token secret (256+ bits) |
| `JWT_ACCESS_EXPIRY` | No | 15m | Access token expiry (e.g., 15m, 1h) |
| `JWT_REFRESH_EXPIRY` | No | 7d | Refresh token expiry (e.g., 7d, 30d) |
| `SENDGRID_API_KEY` | Yes | - | SendGrid API key |
| `EMAIL_FROM` | Yes | - | Verified sender email |
| `CORS_ALLOWED_ORIGINS` | No | * | Comma-separated origins |

## Database Migrations

### Apply Migrations

```bash
# Development
./gradlew flywayMigrate

# Production (via Docker)
docker-compose -f docker-compose.prod.yml exec app ./gradlew flywayMigrate
```

### Check Migration Status

```bash
./gradlew flywayInfo
```

### Rollback Strategy

Flyway doesn't support automatic rollbacks. For rollback:

1. Create a new migration with `DOWN` script
2. Test in staging environment
3. Apply to production

### Migration Best Practices

- ✅ Always test migrations in staging first
- ✅ Backup database before major migrations
- ✅ Use transactional migrations when possible
- ✅ Never modify existing migrations
- ✅ Create new migrations for schema changes

## Monitoring & Observability

### Health Checks

```bash
# Liveness probe (application is running)
curl http://localhost:9000/health

# Readiness probe (application is ready to serve traffic)
curl http://localhost:9000/readiness
```

### Metrics

```bash
# Prometheus metrics
curl http://localhost:9000/actuator/prometheus

# JSON metrics
curl http://localhost:9000/actuator/metrics

# Specific metric
curl http://localhost:9000/actuator/metrics/app.user.registrations
```

### Custom Business Metrics

- `app.user.registrations` - User registration count
- `app.auth.login` - Login attempts (tagged by result)
- `app.todo.operations` - Todo operations (tagged by type)
- `app.email.sent` - Email sending (tagged by result)

See [METRICS.md](docs/METRICS.md) for details.

### Log Aggregation

Application logs in JSON format for easy parsing:

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f app

# Filter errors
docker-compose logs app | grep ERROR

# Export logs
docker-compose logs app > app-logs.txt
```

## Security Checklist

### Before Production

- [ ] Change all default passwords
- [ ] Generate strong JWT secrets (256+ bits)
- [ ] Configure HTTPS/TLS
- [ ] Set CORS to specific domains (not *)
- [ ] Enable firewall rules
- [ ] Set up database backups
- [ ] Configure SendGrid with verified domain
- [ ] Review and harden security headers
- [ ] Enable rate limiting (if using API gateway)
- [ ] Set up monitoring and alerts
- [ ] Perform security scan of dependencies
- [ ] Test disaster recovery plan

### Security Hardening

#### 1. HTTPS/TLS

Use nginx or similar as reverse proxy:

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2. Database Security

```yaml
# PostgreSQL security settings
postgres:
  environment:
    POSTGRES_HOST_AUTH_METHOD: scram-sha-256
  command:
    - "postgres"
    - "-c"
    - "ssl=on"
    - "-c"
    - "ssl_cert_file=/etc/ssl/certs/server.crt"
    - "-c"
    - "ssl_key_file=/etc/ssl/private/server.key"
```

#### 3. Dependency Scanning

```bash
# Check for vulnerable dependencies
./gradlew dependencyCheckAnalyze

# Update dependencies
./gradlew dependencyUpdates
```

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker-compose logs app

# Common issues:
# 1. Database not ready
docker-compose ps postgres

# 2. Missing environment variables
docker-compose config

# 3. Port already in use
lsof -i :9000
```

### Database Connection Issues

```bash
# Test database connection
psql -h localhost -p 5434 -U todo_user -d todo_spring_prod

# Check database logs
docker-compose logs postgres

# Verify network
docker network inspect todo_todo-network
```

### JWT Token Issues

```bash
# Verify JWT secrets are set
docker-compose exec app env | grep JWT

# Check token expiry settings
curl http://localhost:9000/actuator/configprops | grep jwt
```

### Email Not Sending

```bash
# Check SendGrid API key
docker-compose exec app env | grep SENDGRID

# Verify sender email is verified in SendGrid
# Check application logs for email errors
docker-compose logs app | grep email
```

### Performance Issues

```bash
# Check JVM memory
docker stats todo-spring-app-prod

# Review GC logs
docker exec todo-spring-app-prod cat /var/log/gc.log

# Check database connection pool
curl http://localhost:9000/actuator/metrics/hikaricp.connections
```

### Migration Failures

```bash
# Check migration status
./gradlew flywayInfo

# Validate migrations
./gradlew flywayValidate

# Repair checksum issues (careful!)
./gradlew flywayRepair
```

## Backup and Recovery

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U todo_user todo_spring_prod > backup.sql

# Restore
docker-compose exec -T postgres psql -U todo_user todo_spring_prod < backup.sql
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * docker-compose -f /path/to/docker-compose.prod.yml exec postgres pg_dump -U todo_user todo_spring_prod | gzip > /backups/todo-$(date +\%Y\%m\%d).sql.gz
```

## Scaling

### Horizontal Scaling

The application is stateless and can be scaled horizontally:

```bash
# Docker Compose
docker-compose up -d --scale app=3

# Kubernetes
kubectl scale deployment todo-app-spring --replicas=3
```

**Note:** Ensure you have:
- Load balancer configured
- Database connection pool sized appropriately
- Session storage is stateless (JWT-based)

### Vertical Scaling

Adjust container resources:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

## Support

For issues and questions:
- Check logs: `docker-compose logs`
- Review documentation: `README.md`
- Check health endpoints: `/health`, `/readiness`
- Review metrics: `/actuator/prometheus`

## Additional Resources

- [README.md](README.md) - Project overview
- [PHASE6_SUMMARY.md](PHASE6_SUMMARY.md) - Phase 6 implementation details
- [METRICS.md](docs/METRICS.md) - Custom metrics documentation
- [SEEDING.md](docs/SEEDING.md) - Database seeding guide
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
