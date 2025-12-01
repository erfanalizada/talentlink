# TalentLink Deployment Guide

## Overview
Complete deployment guide for TalentLink - AI-powered job recruitment platform with CQRS architecture.

## Architecture Summary

### Backend Services (All with CQRS)
1. **auth-service** (Port 5006) - Keycloak integration, user registration/login
2. **user-service** (Port 5000) - User profile management
3. **job-service** (Port 5001) - Job posting and search
4. **application-service** (Port 5002) - Job applications with event-driven workflow
5. **cv-service** (Port 5003) - CV upload and text extraction
6. **matching-service** (Port 5004) - AI matching with Gemini
7. **notification-service** (Port 5005) - Email notifications via RabbitMQ events

### Infrastructure
- **PostgreSQL**: 7 separate databases (userdb, jobsdb, applicationdb, cvdb, authdb, notificationdb, matchingdb)
- **RabbitMQ**: Event bus for async communication
- **Keycloak**: Authentication and authorization
- **Prometheus + Grafana**: Monitoring
- **Nginx Ingress**: API Gateway and TLS termination

## Prerequisites

1. Oracle Cloud Kubernetes Cluster (OKE) - ✅ Already deployed
2. kubectl configured
3. Docker images built and pushed to GHCR
4. Secrets created (see below)

## Step 1: Create Kubernetes Secrets

```bash
# User Service Database
kubectl create secret generic userdb-secret \
  --from-literal=DATABASE_URL='postgresql://user:password@postgres-host:5432/userdb'

# Job Service Database
kubectl create secret generic jobsdb-secret \
  --from-literal=DATABASE_URL='postgresql://user:password@postgres-host:5432/jobsdb'

# Application Service Database
kubectl create secret generic applicationdb-secret \
  --from-literal=DATABASE_URL='postgresql://user:password@postgres-host:5432/applicationdb'

# CV Service Database
kubectl create secret generic cvdb-secret \
  --from-literal=DATABASE_URL='postgresql://user:password@postgres-host:5432/cvdb'

# Notification Service Database
kubectl create secret generic notificationdb-secret \
  --from-literal=DATABASE_URL='postgresql://user:password@postgres-host:5432/notificationdb'

# RabbitMQ (already exists)
# kubectl get secret rabbitmq-auth

# Gemini API Key
kubectl create secret generic gemini-secret \
  --from-literal=GEMINI_API_KEY='AIzaSyBA9ZHfWSgwLUqnRvDSAwZYWPWB5GuiIXQ'

# Email Configuration (for notifications)
kubectl create secret generic email-secret \
  --from-literal=SMTP_HOST='smtp.gmail.com' \
  --from-literal=SMTP_PORT='587' \
  --from-literal=SMTP_USER='your-email@gmail.com' \
  --from-literal=SMTP_PASSWORD='your-app-password'
```

## Step 2: Deploy PostgreSQL Databases

You already have PostgreSQL deployed. Create additional databases:

```sql
-- Connect to your PostgreSQL instance
CREATE DATABASE userdb;
CREATE DATABASE jobsdb;
CREATE DATABASE applicationdb;
CREATE DATABASE cvdb;
CREATE DATABASE notificationdb;
CREATE DATABASE matchingdb;

-- Create users (optional, or use existing user)
-- GRANT ALL PRIVILEGES ON DATABASE userdb TO your_user;
-- ... repeat for other databases
```

## Step 3: Build and Push Docker Images

```bash
cd backend

# Build all services
for service in shared user-service job-service application-service cv-service matching-service; do
  echo "Building $service..."
  cd $service
  docker build -t ghcr.io/your-username/talentlink-$service:latest .
  docker push ghcr.io/your-username/talentlink-$service:latest
  cd ..
done
```

## Step 4: Deploy Services to Kubernetes

Each service needs a Deployment, Service, and ConfigMap. Example for user-service:

```yaml
# k8s/backend/user-service/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: ghcr.io/your-username/talentlink-user-service:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: userdb-secret
              key: DATABASE_URL
        - name: RABBITMQ_URL
          valueFrom:
            secretKeyRef:
              name: rabbitmq-auth
              key: url
        - name: KEYCLOAK_URL
          value: "https://talentlink-erfan.nl/auth"
        - name: KEYCLOAK_REALM
          value: "talentlink"
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: default
spec:
  selector:
    app: user-service
  ports:
  - port: 5000
    targetPort: 5000
  type: ClusterIP
```

Apply all manifests:

```bash
kubectl apply -f k8s/backend/user-service/
kubectl apply -f k8s/backend/job-service/
kubectl apply -f k8s/backend/application-service/
kubectl apply -f k8s/backend/cv-service/
kubectl apply -f k8s/backend/matching-service/
kubectl apply -f k8s/backend/notification-service/
```

## Step 5: Deploy Monitoring Stack

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Default credentials: admin / prom-operator
```

## Step 6: Configure Ingress

Your ingress is already configured at `k8s/ingress.yaml`. Verify it includes all services:

```bash
kubectl get ingress talentlink-ingress -o yaml
```

## Step 7: Deploy Flutter Frontend

```bash
cd frontend/talentlink_frontend

# Build for web
flutter build web --release

# Create Docker image
docker build -t ghcr.io/your-username/talentlink-frontend:latest .
docker push ghcr.io/your-username/talentlink-frontend:latest

# Deploy to Kubernetes
kubectl apply -f ../../k8s/frontend/
```

## Step 8: Configure Keycloak

1. Access Keycloak: https://talentlink-erfan.nl/auth
2. Login with admin credentials
3. Create realm: `talentlink`
4. Create roles: `employee`, `employer`
5. Create client: `frontend-client`
   - Client Protocol: openid-connect
   - Access Type: public
   - Valid Redirect URIs: `https://talentlink-erfan.nl/*`
   - Web Origins: `https://talentlink-erfan.nl`
6. Create client: `auth-service`
   - Access Type: confidential
   - Service Accounts Enabled: On

## Step 9: Verify Deployment

```bash
# Check all pods are running
kubectl get pods

# Check services
kubectl get svc

# Check ingress
kubectl get ingress

# Test health endpoints
curl https://talentlink-erfan.nl/api/users/health
curl https://talentlink-erfan.nl/api/jobs/health
curl https://talentlink-erfan.nl/api/applications/health
curl https://talentlink-erfan.nl/api/cv/health
curl https://talentlink-erfan.nl/api/matching/health

# Check Prometheus metrics
curl https://talentlink-erfan.nl/api/users/metrics
```

## Step 10: Test End-to-End Flow

### Employee Flow:
1. Register as employee → POST /api/auth/register
2. Login → POST /api/auth/login
3. Create profile → POST /api/users
4. Upload CV → POST /api/cv/upload
5. Browse jobs → GET /api/jobs
6. Apply to job → POST /api/applications
7. View applications → GET /api/applications/my-applications

### Employer Flow:
1. Register as employer → POST /api/auth/register
2. Login → POST /api/auth/login
3. Create profile → POST /api/users
4. Post job → POST /api/jobs
5. View my jobs → GET /api/jobs/my-jobs
6. View applications → GET /api/applications/job/{job_id}
7. Invite candidate → POST /api/applications/{id}/invite

## Monitoring

### Prometheus Queries
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Request latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# CQRS commands
rate(cqrs_commands_total[5m])

# Events published
rate(events_published_total[5m])
```

### Grafana Dashboards
1. System Overview - CPU, Memory, Pods
2. API Performance - Latency, Request Rate, Error Rate
3. CQRS Metrics - Commands, Queries, Events
4. Database Connections - Active connections per service

## Troubleshooting

### Common Issues

**1. Pod not starting**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**2. Database connection issues**
```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql postgresql://user:password@postgres-host:5432/userdb
```

**3. RabbitMQ connection issues**
```bash
# Check RabbitMQ management UI
https://talentlink-erfan.nl/rabbitmq

# Check RabbitMQ logs
kubectl logs <rabbitmq-pod-name>
```

**4. Keycloak authentication issues**
```bash
# Test Keycloak endpoint
curl https://talentlink-erfan.nl/auth/realms/talentlink

# Check Keycloak logs
kubectl logs <keycloak-pod-name>
```

**5. Gemini API issues**
```bash
# Test Gemini API
curl https://talentlink-erfan.nl/api/matching/test-gemini
```

## Scaling

```bash
# Scale specific service
kubectl scale deployment user-service --replicas=3

# Auto-scaling (HPA)
kubectl autoscale deployment user-service --cpu-percent=70 --min=2 --max=10
```

## Backup and Recovery

```bash
# Backup PostgreSQL
kubectl exec -it <postgres-pod> -- pg_dump -U user dbname > backup.sql

# Backup RabbitMQ definitions
# Via management UI: Overview → Export definitions
```

## Security Checklist

- ✅ HTTPS enforced via ingress
- ✅ JWT authentication on all endpoints
- ✅ Role-based access control (RBAC)
- ✅ Secrets stored in Kubernetes secrets
- ✅ Database credentials rotated regularly
- ✅ Network policies (optional - add if needed)
- ✅ Pod security policies

## Performance Optimization

1. **Enable caching** - Add Redis for frequently accessed data
2. **Database indexing** - All foreign keys and frequently queried fields indexed
3. **Connection pooling** - SQLAlchemy pool configured
4. **Async processing** - RabbitMQ for long-running tasks
5. **CDN** - Use CDN for frontend static assets

## CI/CD Pipeline

See `.github/workflows/` for GitHub Actions pipelines:
- Build and push Docker images
- Deploy to Kubernetes via kubectl
- Run tests
- Security scanning

## Support and Maintenance

- **Logs**: `kubectl logs -f <pod-name>`
- **Metrics**: Grafana dashboards
- **Alerts**: Configure Prometheus alerting rules
- **Updates**: Use ArgoCD for GitOps deployments

## API Documentation

API docs available at:
- Swagger UI (optional): `/api/docs`
- Or use Postman collection (create one)

## Next Steps

1. ✅ All backend services deployed
2. ⏳ Frontend Flutter app needs to be completed
3. ⏳ Email service configuration for notifications
4. ⏳ CI/CD pipeline setup
5. ⏳ Production monitoring and alerting
6. ⏳ Load testing and performance tuning
