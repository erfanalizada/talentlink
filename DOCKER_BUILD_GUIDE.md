# Docker Build Guide for TalentLink

## The Problem (Fixed)

The original Dockerfiles had:
```dockerfile
COPY ../shared /app/shared  # ❌ This fails - can't access parent directory
```

Docker builds can't access files outside the build context using `../`.

## The Solution

### 1. Fixed Dockerfiles

All Dockerfiles now use paths relative to the **backend/** directory as the build context:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy shared library (from backend/shared)
COPY shared/ /app/shared/

# Copy service files (from backend/service-name)
COPY user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY user-service/ .

EXPOSE 5000
CMD ["python", "app.py"]
```

### 2. Build from Backend Directory

**IMPORTANT**: Always build from the `backend/` directory:

```bash
# ✅ Correct way
cd backend
docker build -f user-service/Dockerfile -t talentlink-user-service .

# ❌ Wrong way (will fail)
cd backend/user-service
docker build -t talentlink-user-service .
```

## Manual Build Instructions

### Build All Services Locally

```bash
cd backend

# Build user-service
docker build -f user-service/Dockerfile \
  -t ghcr.io/YOUR_USERNAME/talentlink-user-service:latest .

# Build job-service
docker build -f job-service/Dockerfile \
  -t ghcr.io/YOUR_USERNAME/talentlink-job-service:latest .

# Build application-service
docker build -f application-service/Dockerfile \
  -t ghcr.io/YOUR_USERNAME/talentlink-application-service:latest .

# Build cv-service
docker build -f cv-service/Dockerfile \
  -t ghcr.io/YOUR_USERNAME/talentlink-cv-service:latest .

# Build matching-service
docker build -f matching-service/Dockerfile \
  -t ghcr.io/YOUR_USERNAME/talentlink-matching-service:latest .
```

### Push to GitHub Container Registry

```bash
# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Push all images
docker push ghcr.io/YOUR_USERNAME/talentlink-user-service:latest
docker push ghcr.io/YOUR_USERNAME/talentlink-job-service:latest
docker push ghcr.io/YOUR_USERNAME/talentlink-application-service:latest
docker push ghcr.io/YOUR_USERNAME/talentlink-cv-service:latest
docker push ghcr.io/YOUR_USERNAME/talentlink-matching-service:latest
```

## GitHub Actions Workflow

The workflow is now configured correctly:

```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: ./backend          # ✅ Build context is backend/
    file: ./backend/user-service/Dockerfile  # ✅ Dockerfile path
    platforms: linux/amd64,linux/arm64
    push: true
```

### Key Points:
- `context: ./backend` - Sets build context to backend directory
- `file: ./backend/user-service/Dockerfile` - Path to Dockerfile from repo root
- Dockerfile uses `COPY shared/` and `COPY user-service/` relative to context

## File Structure

```
talentlink/
├── backend/                    ← Build context
│   ├── shared/                ← Copied with: COPY shared/
│   ├── user-service/          ← Copied with: COPY user-service/
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   └── requirements.txt
│   ├── job-service/
│   ├── application-service/
│   ├── cv-service/
│   └── matching-service/
└── .github/workflows/
```

## Troubleshooting

### Error: "shared: not found"
**Cause**: Building from wrong directory
**Solution**: Build from `backend/` directory, not from service subdirectory

### Error: "requirements.txt: not found"
**Cause**: Wrong COPY path in Dockerfile
**Solution**: Use `COPY user-service/requirements.txt .` not `COPY requirements.txt .`

### Error: "permission denied" when pushing
**Cause**: Not authenticated to GHCR
**Solution**:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

### Error: "manifest unknown" when pulling
**Cause**: Image doesn't exist or is private
**Solution**: Make package public in GitHub settings or add imagePullSecret to K8s

## GitHub Actions Setup

### Required Secrets

Add to your GitHub repository Settings → Secrets and variables → Actions:

1. **KUBE_CONFIG** (for deployment workflow)
   ```bash
   # Get your kubeconfig and base64 encode it
   cat ~/.kube/config | base64 -w 0
   ```
   Paste the output as KUBE_CONFIG secret

2. **GITHUB_TOKEN** (automatic, no setup needed)
   - Used for pushing to GHCR
   - Automatically available in GitHub Actions

### Enable GitHub Container Registry

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Create token with `write:packages` permission
3. Or use automatic `GITHUB_TOKEN` (already has permissions)

### Make Images Public (Optional)

After first push:
1. Go to github.com/YOUR_USERNAME?tab=packages
2. Click on package (e.g., talentlink-user-service)
3. Package settings → Change visibility → Public

## Testing Locally

### Run Service Locally

```bash
cd backend

# Build
docker build -f user-service/Dockerfile -t test-user-service .

# Run
docker run -p 5000:5000 \
  -e DATABASE_URL='postgresql://...' \
  -e RABBITMQ_URL='amqp://...' \
  -e KEYCLOAK_URL='https://talentlink-erfan.nl/auth' \
  test-user-service

# Test
curl http://localhost:5000/health
```

## Quick Commands

```bash
# Build all services
cd backend
for service in user job application cv matching; do
  docker build -f ${service}-service/Dockerfile \
    -t ghcr.io/erfanmoghadasi/talentlink-${service}-service:latest .
done

# Push all (after docker login)
for service in user job application cv matching; do
  docker push ghcr.io/erfanmoghadasi/talentlink-${service}-service:latest
done
```

## Multi-Platform Builds

GitHub Actions builds for both amd64 and arm64:

```yaml
platforms: linux/amd64,linux/arm64
```

For local multi-platform builds:
```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 \
  -f user-service/Dockerfile \
  -t ghcr.io/YOUR_USERNAME/talentlink-user-service:latest \
  --push .
```

## Summary

✅ **Fixed**: All Dockerfiles now work with proper build context
✅ **GitHub Actions**: Configured to build from `backend/` directory
✅ **Multi-platform**: Builds for both amd64 and arm64
✅ **Automated**: Pushes to GHCR and deploys to Kubernetes

The key fix was changing the build context to `backend/` directory and updating Dockerfile COPY commands to use relative paths from that context.
