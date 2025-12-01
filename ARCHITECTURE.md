# TalentLink Architecture

## System Overview
TalentLink is a microservices-based job recruitment platform with CQRS pattern, event-driven architecture, and AI-powered candidate matching.

## Architecture Pattern: CQRS + Event Sourcing

### Core Principles
1. **Command Query Responsibility Segregation (CQRS)**: Separate read and write operations
2. **Event-Driven**: Services communicate via RabbitMQ events
3. **Domain-Driven Design**: Clear bounded contexts per service
4. **Eventual Consistency**: Async processing for scalability

## Microservices

### 1. User Service
**Port**: 5000
**Database**: `userdb` (PostgreSQL)
**Responsibilities**:
- User profile management (employee/employer)
- User preferences and settings
- CQRS: Commands (CreateProfile, UpdateProfile) | Queries (GetProfile, ListUsers)

### 2. Job Service
**Port**: 5001
**Database**: `jobsdb` (PostgreSQL)
**Responsibilities**:
- Job posting CRUD (employers only)
- Job search and filtering (employees)
- CQRS: Commands (CreateJob, UpdateJob, DeleteJob) | Queries (GetJob, SearchJobs, GetEmployerJobs)

### 3. Application Service
**Port**: 5002
**Database**: `applicationdb` (PostgreSQL)
**Responsibilities**:
- Job application submissions
- Application status management
- CQRS: Commands (SubmitApplication, UpdateStatus, InviteCandidate) | Queries (GetApplications, GetApplicationsByJob)
- Events: ApplicationSubmitted, ApplicationStatusChanged, CandidateInvited

### 4. CV Service
**Port**: 5003
**Storage**: File system (persistent volume)
**Database**: `cvdb` (PostgreSQL) - metadata
**Responsibilities**:
- CV upload (PDF, DOC, DOCX)
- CV storage and retrieval
- CV text extraction
- CQRS: Commands (UploadCV, DeleteCV) | Queries (GetCV, GetCVMetadata)

### 5. Matching Service (AI)
**Port**: 5004
**External API**: Google Gemini
**Responsibilities**:
- AI-powered CV analysis using Gemini
- Job-candidate matching score (0-100%)
- Skill extraction and comparison
- Match explanation generation
- CQRS: Commands (AnalyzeCV) | Queries (GetMatchScore, GetMatchDetails)

### 6. Notification Service
**Port**: 5005
**Database**: `notificationdb` (PostgreSQL)
**Responsibilities**:
- Email notifications (interview invitations, status updates)
- Event consumption from RabbitMQ
- CQRS: Commands (SendEmail, MarkAsRead) | Queries (GetNotifications)
- Listens to: ApplicationSubmitted, CandidateInvited events

### 7. Auth Service (Existing)
**Port**: 5006
**Integration**: Keycloak
**Responsibilities**:
- User registration (employee/employer roles)
- Login/logout via Keycloak
- Token validation
- Role management

## Event Bus (RabbitMQ)

### Exchanges
- `talentlink.events` (topic exchange)

### Events
```json
{
  "ApplicationSubmitted": {
    "application_id": "uuid",
    "job_id": "uuid",
    "user_id": "uuid",
    "timestamp": "iso8601"
  },
  "ApplicationStatusChanged": {
    "application_id": "uuid",
    "old_status": "pending",
    "new_status": "invited",
    "changed_by": "uuid"
  },
  "CandidateInvited": {
    "application_id": "uuid",
    "candidate_email": "string",
    "job_title": "string",
    "employer_name": "string"
  },
  "CVUploaded": {
    "cv_id": "uuid",
    "user_id": "uuid",
    "file_path": "string"
  }
}
```

## Database Schema

### userdb.users
```sql
id UUID PRIMARY KEY
keycloak_id VARCHAR(255) UNIQUE
email VARCHAR(255) UNIQUE
full_name VARCHAR(255)
role VARCHAR(50) -- 'employee' or 'employer'
company_name VARCHAR(255) -- for employers
created_at TIMESTAMP
updated_at TIMESTAMP
```

### jobsdb.jobs
```sql
id UUID PRIMARY KEY
employer_id UUID REFERENCES users(id)
title VARCHAR(255)
description TEXT
company_name VARCHAR(255)
required_skills JSONB -- array of skills
required_technologies JSONB -- array of technologies
experience_years INTEGER
location VARCHAR(255)
employment_type VARCHAR(50) -- full-time, part-time, contract
status VARCHAR(50) -- active, closed
created_at TIMESTAMP
updated_at TIMESTAMP
```

### applicationdb.applications
```sql
id UUID PRIMARY KEY
job_id UUID
employee_id UUID
cv_id UUID
status VARCHAR(50) -- pending, reviewed, invited, rejected
match_score INTEGER -- 0-100
match_summary TEXT
applied_at TIMESTAMP
updated_at TIMESTAMP
```

### cvdb.cvs
```sql
id UUID PRIMARY KEY
user_id UUID
file_name VARCHAR(255)
file_path VARCHAR(500)
file_size BIGINT
content_type VARCHAR(100)
extracted_text TEXT
uploaded_at TIMESTAMP
```

### notificationdb.notifications
```sql
id UUID PRIMARY KEY
user_id UUID
type VARCHAR(50) -- email, in_app
subject VARCHAR(255)
body TEXT
read BOOLEAN DEFAULT FALSE
sent_at TIMESTAMP
```

## Monitoring Stack (Lightweight)

### Prometheus
- Metrics collection from all services
- Custom metrics: API latency, request count, error rate
- Scrape interval: 15s

### Grafana
- Dashboards for each service
- System health overview
- Alert rules for critical metrics

### Loki (Optional)
- Log aggregation
- Minimal resource footprint

## API Gateway Pattern
- Nginx Ingress Controller handles routing
- Path-based routing: `/api/{service}`
- TLS termination at ingress

## Security
- Keycloak JWT tokens for authentication
- Role-based access control (RBAC)
- HTTPS only (enforced)
- CORS enabled for frontend

## Deployment
- Kubernetes on Oracle Cloud
- Docker containers for each service
- GitHub Actions CI/CD
- ArgoCD for GitOps (already configured)
- Secrets managed via Kubernetes secrets

## Tech Stack
- **Backend**: Python 3.11+ with Flask
- **Frontend**: Flutter Web (Material Design 3)
- **Databases**: PostgreSQL 15+
- **Message Queue**: RabbitMQ 3.12+
- **Auth**: Keycloak
- **AI**: Google Gemini API
- **Monitoring**: Prometheus + Grafana
- **Container**: Docker
- **Orchestration**: Kubernetes (OKE)
- **Ingress**: Nginx Ingress Controller
- **CI/CD**: GitHub Actions + ArgoCD
