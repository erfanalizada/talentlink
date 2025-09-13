# CareerBridge  
*A cloud-native web application built with Flutter, Kubernetes, and Keycloak that connects students and professionals with employers.*

---

## 📌 Project Overview  
CareerBridge is a hiring platform where:  
- **Employees (students & professionals)** can create an account, build a profile, upload their CV, and set their job availability.  
- **Employers (companies)** can register with a verified company email, post job advertisements (Internships, Graduation Internships, and Jobs), and use a **matching engine** to find the best candidates.  

The system automatically matches job descriptions with employee CVs and profiles, helping employers quickly identify suitable candidates. Both sides can communicate through integrated email notifications.  

---

## 🚀 Core Features  
- 🔑 **Authentication & Security**: Role-based login (Employee/Employer) with **Keycloak** and MFA (Google Authenticator).  
- 👤 **Employee Dashboard**: Profile management, CV upload, availability toggle (Open/Closed).  
- 🏢 **Employer Dashboard**: Job posting (Internship, Graduation Internship, Job) with description and logo.  
- 🔍 **Matching Engine**: Text-based similarity search (BM25 / Postgres full-text search), filters by availability and job type.  
- 📧 **Notifications**: Email workflows for job applications and employer offers.  
- 🛡 **GDPR Compliance**: Users can delete or export their data.  

---

## 🛠️ Technology Stack  
- **Frontend**: Flutter Web  
- **Backend**: FastAPI (Python) / Node.js (Express)  
- **Authentication**: Keycloak (OIDC, MFA)  
- **Database**: PostgreSQL  
- **Storage**: MinIO (CVs, images)  
- **Search**: PostgreSQL full-text search (optionally OpenSearch/pgvector)  
- **Orchestration**: Docker + Kubernetes (Minikube/k3d for development)  
- **CI/CD**: GitHub Actions  
- **Monitoring**: Prometheus + Grafana + Loki  

---

## 🎯 Learning Outcomes Demonstrated  
This project demonstrates:  
- **LO1 – Professional Standard**: Documentation, ADRs, structured methodology, stakeholder focus.  
- **LO2 – Personal Leadership**: Goal setting, reflection, feedback loop in project logs.  
- **LO3 – Scalable Architectures**: Modular architecture, scalable database & search.  
- **LO4 – DevOps**: CI/CD pipelines, Infrastructure as Code, automated testing & deployment.  
- **LO5 – Cloud Native**: Kubernetes-based deployment, cloud-ready services, cost-awareness.  
- **LO6 – Security by Design**: Keycloak authentication, MFA, GDPR features, secure file handling.  
- **LO7 – Distributed Data**: PostgreSQL, MinIO, and search services with replication & indexing.  

---

## 📂 Repository Structure  
