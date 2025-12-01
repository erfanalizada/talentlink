# TalentLink - AI-Powered Job Recruitment Platform

**Complete microservices-based recruitment platform with CQRS, event-driven architecture, and AI-powered candidate matching.**

## 🎯 Features

### For Employees
- ✅ Register/Login via Keycloak
- ✅ Upload CV (PDF, DOC, DOCX)
- ✅ Browse active ICT job postings
- ✅ One-click job applications
- ✅ View application status with AI match scores (0-100%)
- ✅ Email notifications for interview invitations

### For Employers
- ✅ Register/Login via Keycloak
- ✅ Post job openings with requirements
- ✅ View all posted jobs
- ✅ See applications sorted by AI match score
- ✅ Download candidate CVs
- ✅ AI-generated candidate match analysis
- ✅ Send interview invitations

## 🏗️ Architecture

### Backend Services (CQRS Pattern)
All backend services implement **Command Query Responsibility Segregation (CQRS)** with event-driven communication via RabbitMQ.

| Service | Port | Database | Purpose |
|---------|------|----------|---------|
| **auth-service** | 5006 | authdb | Keycloak integration, user authentication |
| **user-service** | 5000 | userdb | User profile management (employee/employer) |
| **job-service** | 5001 | jobsdb | Job posting CRUD and search |
| **application-service** | 5002 | applicationdb | Job applications with event workflow |
| **cv-service** | 5003 | cvdb | CV upload, storage, text extraction |
| **matching-service** | 5004 | - | AI matching with Google Gemini |
| **notification-service** | 5005 | notificationdb | Email notifications via events |

### Technology Stack

**Backend:**
- Python 3.11+ with Flask
- CQRS pattern with custom framework
- PostgreSQL (7 separate databases)
- RabbitMQ (event bus)
- Google Gemini AI
- Prometheus metrics in all services

**Frontend:**
- Flutter Web with Material Design 3
- Keycloak authentication
- REST API integration

**Infrastructure:**
- Kubernetes (Oracle Cloud OKE)
- Docker containers
- Nginx Ingress Controller
- TLS with Let's Encrypt
- Prometheus + Grafana monitoring
- GitHub Actions CI/CD

## 📁 Project Structure

```
talentlink/
├── backend/
│   ├── shared/                      # Shared CQRS library
│   ├── user-service/               # User profile management (CQRS)
│   ├── job-service/                # Job posting and search (CQRS)
│   ├── application-service/        # Job applications (CQRS + Events)
│   ├── cv-service/                 # CV upload and extraction
│   ├── matching-service/           # AI matching with Gemini
│   ├── auth-service/               # Keycloak integration
│   └── notification-service/       # Email notifications
├── frontend/talentlink_frontend/   # Flutter web app
├── k8s/                            # Kubernetes manifests
├── infra/                          # Terraform for OCI
├── ARCHITECTURE.md                 # Detailed architecture
├── DEPLOYMENT_GUIDE.md             # Deployment instructions
└── README.md                       # This file
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd talentlink
```

### 2. Deploy to Kubernetes
```bash
# Create secrets (see DEPLOYMENT_GUIDE.md for details)
kubectl create secret generic gemini-secret \
  --from-literal=GEMINI_API_KEY='AIzaSyBA9ZHfWSgwLUqnRvDSAwZYWPWB5GuiIXQ'

# Deploy services
kubectl apply -f k8s/backend/user/
kubectl apply -f k8s/backend/job/
kubectl apply -f k8s/backend/application/
kubectl apply -f k8s/backend/cv/
kubectl apply -f k8s/backend/matching/

# Deploy ingress
kubectl apply -f k8s/ingress-updated.yaml
```

### 3. Verify
```bash
curl https://talentlink-erfan.nl/api/users/health
curl https://talentlink-erfan.nl/api/jobs/health
```

## 📖 API Documentation

### Employee Flow
```bash
# 1. Register
POST /api/auth/register
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "employee"
}

# 2. Login
POST /api/auth/login

# 3. Upload CV
POST /api/cv/upload (multipart/form-data)

# 4. Browse jobs
GET /api/jobs

# 5. Apply
POST /api/applications
{
  "job_id": "uuid",
  "cv_id": "uuid"
}

# 6. View applications
GET /api/applications/my-applications
```

### Employer Flow
```bash
# 1. Register
POST /api/auth/register (role: "employer")

# 2. Post job
POST /api/jobs
{
  "title": "Senior Python Developer",
  "description": "...",
  "company_name": "Tech Corp",
  "required_skills": ["Python", "Django"],
  "required_technologies": ["Docker", "AWS"],
  "experience_years": 5,
  "location": "Amsterdam",
  "employment_type": "full-time"
}

# 3. View applications
GET /api/applications/job/{job_id}

# 4. Invite candidate
POST /api/applications/{id}/invite
```

## 🔧 CQRS Implementation

All services follow CQRS pattern with:
- **Commands** for write operations (CreateJob, SubmitApplication)
- **Queries** for read operations (GetJobs, GetApplications)
- **Events** published to RabbitMQ (ApplicationSubmitted, CandidateInvited)

Example:
```python
# Command
@dataclass
class CreateJobCommand(Command):
    employer_id: str
    title: str
    description: str

# Handler
class CreateJobHandler(CommandHandler):
    async def handle(self, command: CreateJobCommand) -> Result:
        # Create job in database
        # Publish JobCreatedEvent
        # Return result
```

## 📊 Monitoring

All services expose Prometheus metrics at `/metrics`:
- Request rate, latency, error rate
- CQRS commands and queries executed
- Events published to RabbitMQ

Access Grafana:
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Credentials: admin / prom-operator
```

## 🔐 Security

- HTTPS enforced
- JWT authentication with Keycloak
- Role-based access control (employee/employer)
- Secrets managed via Kubernetes
- Input validation on all endpoints

## 📚 Documentation

- **ARCHITECTURE.md** - System design and patterns
- **DEPLOYMENT_GUIDE.md** - Step-by-step deployment
- Service READMEs in each backend service directory

## 🚧 Remaining Work

### Backend (✅ Complete)
- ✅ All services with CQRS pattern
- ✅ Event-driven communication
- ✅ AI matching with Gemini
- ✅ Monitoring with Prometheus

### Frontend (⏳ In Progress)
- ⏳ Flutter web application
- ⏳ Employee dashboard
- ⏳ Employer dashboard
- ⏳ Material Design UI

### DevOps
- ⏳ CI/CD pipelines
- ⏳ ArgoCD GitOps
- ⏳ Production monitoring alerts

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement with CQRS pattern
4. Add tests and metrics
5. Submit Pull Request

## 👥 Team

Developed by Erfan Moghadasi

## 📞 Support

- Issues: GitHub Issues
- Email: support@talentlink.com

---

**Base URL**: https://talentlink-erfan.nl

**RabbitMQ**: https://talentlink-erfan.nl/rabbitmq

**Keycloak**: https://talentlink-erfan.nl/auth

**Gemini API Key**: AIzaSyBA9ZHfWSgwLUqnRvDSAwZYWPWB5GuiIXQ
