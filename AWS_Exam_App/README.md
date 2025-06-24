# 🚀 GitOps Projects Repository

![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-blue?style=for-the-badge&logo=argo)
![CI/CD](https://img.shields.io/badge/CI%2FCD-Jenkins-D24939?style=for-the-badge&logo=jenkins)
![Kubernetes](https://img.shields.io/badge/Kubernetes-K3s-326CE5?style=for-the-badge&logo=kubernetes)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-Flask-3776AB?style=for-the-badge&logo=python&logoColor=white)

**Comprehensive collection of GitOps implementations, CI/CD pipelines, and DevOps automation projects**

---

## 🎯 Interactive Architecture Overview

### 📊 **[Live GitOps Architecture Diagram](https://sohaib1khan.github.io/GitOps_Projects/)**

Experience our complete GitOps pipeline through an interactive, multi-tab visualization:

<div align="center">

**[🔗 View Interactive Diagram](https://sohaib1khan.github.io/GitOps_Projects/)**

*Click above to explore the full architecture with interactive components*

</div>

The diagram showcases:
- **🔧 Development & CI Layer**: GitHub, Jenkins, DockerHub integration
- **🚀 GitOps & CD Layer**: ArgoCD, Kubernetes API, Webhook automation  
- **☸️ Runtime & Storage Layer**: K3s cluster, MetalLB, Persistent storage
- **💾 Data Flow Management**: Complete data persistence strategy

---

## 🏗️ Repository Structure

```
GitOps_Projects/
├── 📊 docs/                          # Interactive architecture diagram
│   └── index.html                    # Live GitOps visualization
├── 🐍 AWS_Exam_App/                  # Flask application examples
├── 🔗 DashLink/                      # Dashboard applications  
├── 🚀 deploy_to_remote_machine/      # Remote deployment scripts
├── 🔧 jenkins/                       # Jenkins pipeline configurations
└── 📖 README.md                      # This comprehensive guide
```


## 🚀 Complete GitOps Workflow

### **Automated Development Pipeline**

```mermaid
graph LR
    A[👨‍💻 Code Push] --> B[🔔 GitHub Webhook]
    B --> C[🔧 Jenkins Build]
    C --> D[🐳 Docker Image]
    D --> E[📦 DockerHub Push]
    E --> F[👁️ ArgoCD Detection]
    F --> G[🔄 Auto Sync]
    G --> H[☸️ K8s Deployment]
    H --> I[🌐 Live Application]
```

### **Real-World Implementation**

1. **📝 Code Changes** → Developer pushes to GitHub repository
2. **🔔 Webhook Trigger** → GitHub automatically notifies Jenkins
3. **🔧 CI Pipeline** → Jenkins builds, tests, and containerizes application
4. **📦 Image Registry** → Automated push to DockerHub with versioning
5. **👁️ GitOps Detection** → ArgoCD monitors Git for infrastructure changes
6. **🔄 Automated Sync** → ArgoCD deploys changes to Kubernetes cluster
7. **🌐 Live Deployment** → Application accessible via MetalLB LoadBalancer

---

## 🛠️ Infrastructure & Environment

### **Homelab Architecture**
- **🖥️ Proxmox Virtualization** - Enterprise-grade hypervisor platform
- **☸️ K3s Kubernetes Cluster** - Lightweight, production-ready orchestration
- **🔧 Jenkins CI/CD Server** - Automated pipeline execution environment
- **🚀 ArgoCD GitOps Operator** - Declarative continuous delivery
- **⚖️ MetalLB Load Balancer** - External service exposure for bare-metal

### **Persistent Data Management**
- **💾 Host Path Storage** - Direct node storage mounting
- **🔄 Init Container Strategy** - Automated data initialization
- **📁 Volume Mount Configuration** - Persistent file system integration
- **🛡️ Data Protection** - Survives pod restarts and deployments

---

## 📚 Featured Projects

### **1. Flask GitOps Application**
**Tech Stack**: Python, Flask, Docker, Kubernetes, Jenkins, ArgoCD

Complete web application with:
- RESTful API endpoints with health checks
- Persistent data storage with JSON file management
- Automated CI/CD pipeline with GitHub integration
- GitOps deployment with ArgoCD synchronization
- Production-ready Kubernetes manifests

**Key Features**:
- 🔒 Secure container configuration with non-root user
- 📊 Health monitoring and readiness probes
- 🔄 Rolling update deployment strategy
- 💾 Data persistence across deployments
- 🌐 LoadBalancer service with MetalLB integration

### **2. AWS Exam Application**
**Purpose**: Cloud certification preparation platform
- Interactive study materials and progress tracking
- Containerized deployment with persistent user data
- CI/CD integration for continuous content updates


## 🔧 Quick Start Guide

### **Prerequisites**
- Kubernetes/K3s cluster running
- Jenkins with Docker and kubectl access
- ArgoCD installed and configured
- DockerHub account for image registry
- GitHub repository with webhook capabilities

### **Deployment Commands**

```bash
# Clone the repository
git clone https://github.com/sohaib1khan/GitOps_Projects.git
cd GitOps_Projects/AWS_Exam_App

# Deploy data persistence layer (one-time setup)
kubectl apply -f k8s/data-setup.yaml

# Deploy application via GitOps
kubectl apply -f k8s/deployment.yaml

# Verify deployment status
kubectl get pods,svc -n flask-gitops

# Access application
curl http://YOUR_LOAD_BALANCER_IP
```

### **Pipeline Configuration**

1. **Jenkins Setup**: Configure DockerHub and GitHub credentials
2. **ArgoCD Application**: Point to your repository's k8s/ directory
3. **GitHub Webhook**: Enable automatic build triggers
4. **Load Balancer**: Configure MetalLB IP range for service exposure

---

## 📈 Monitoring & Operations

### **Health Monitoring**
```bash
# Check application status
kubectl get pods -n flask-gitops

# View application logs
kubectl logs -f deployment/flask-app -n flask-gitops

# Monitor ArgoCD sync status
kubectl get applications -n argocd
```

### **Troubleshooting**
```bash
# Debug pod issues
kubectl describe pod -l app=flask-app -n flask-gitops

# Check persistent storage
ls -la /home/k8server/FlaskGitOpsData/

# Verify ArgoCD repository connection
argocd repo list
```


---

---
<div align="center">

### **🚀 Transforming Infrastructure Through Code**


**[🔗 Explore the Interactive Architecture](https://sohaib1khan.github.io/GitOps_Projects/)**

</div>

---
