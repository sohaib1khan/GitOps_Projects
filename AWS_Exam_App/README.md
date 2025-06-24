# Complete GitOps Setup Guide for Flask Applications

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Docker Configuration](#docker-configuration)
4. [Kubernetes Setup with Data Separation](#kubernetes-setup-with-data-separation)
5. [Jenkins CI Pipeline](#jenkins-ci-pipeline)
6. [ArgoCD Configuration](#argocd-configuration)
7. [GitHub Integration](#github-integration)
8. [Complete GitOps Workflow](#complete-gitops-workflow)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance & Updates](#maintenance--updates)

---

## Prerequisites

### Infrastructure Requirements
- ✅ **Kubernetes/K3s cluster** running
- ✅ **MetalLB** for LoadBalancer services
- ✅ **Jenkins** installed and accessible
- ✅ **ArgoCD** installed and accessible
- ✅ **Docker** installed on Jenkins agent
- ✅ **kubectl** access from Jenkins
- ✅ **Git repository** (GitHub/GitLab)

### Access Requirements
- 🔑 **DockerHub account** (private repository)
- 🔑 **GitHub Personal Access Token**
- 🔑 **Jenkins admin access**
- 🔑 **ArgoCD admin access**
- 🔑 **Kubernetes cluster admin access**

### Network Setup
- 📡 **Persistent Volume path** available on K8s nodes
- 📡 **Load Balancer IP range** configured
- 📡 **Jenkins accessible** (for GitHub webhooks)

---

## Project Structure

### Recommended Directory Layout
```
your-flask-app/
├── Dockerfile                    # Docker build configuration
├── Jenkinsfile                   # CI pipeline definition
├── main.py                       # Flask application
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── k8s/                         # Kubernetes manifests
│   ├── data-setup.yaml          # One-time data initialization
│   └── deployment.yaml          # Application deployment
├── static/                      # Static web assets
│   └── css/
│       └── style.css
├── templates/                   # Flask HTML templates
│   ├── base.html
│   ├── index.html
│   └── ...
├── flashcard_progress.json      # Default data files
├── flashcards.json              # (optional - for Docker build)
├── progress.json
├── questions.json
└── users.json
```

### Key Files Purpose
- **`Dockerfile`**: Builds application container image
- **`Jenkinsfile`**: Defines CI/CD pipeline stages
- **`k8s/data-setup.yaml`**: One-time persistent data setup
- **`k8s/deployment.yaml`**: Application deployment (managed by GitOps)
- **JSON files**: Default application data for initial setup

---

## Docker Configuration

### Create Optimized Dockerfile

```dockerfile
# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and assets
COPY main.py .
COPY templates/ ./templates/
COPY static/ ./static/

# Copy default JSON data files (create minimal ones if missing)
COPY *.json ./

# Expose the port the app runs on
EXPOSE 5019

# Command to run the application
CMD ["python", "main.py"]
```

### Create Minimal Default JSON Files

If your JSON files are missing, create minimal defaults:

```bash
# Create minimal default files for Docker build
echo '{"admin": "admin123", "demo": "demo"}' > users.json
echo '[]' > questions.json
echo '[]' > flashcards.json  
echo '{}' > progress.json
echo '{}' > flashcard_progress.json
```

### Test Docker Build

```bash
# Build and test locally
docker build -t your-app:test .
docker run -p 5019:5019 your-app:test

# Test the application
curl http://localhost:5019
```

---

## Kubernetes Setup with Data Separation

### Step 1: Create Data Management Setup

**File: `k8s/data-setup.yaml`**

```yaml
# =====================================================
# DATA MANAGEMENT - Deploy this ONCE manually
# This manages persistent data separately from app deployment
# =====================================================
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: initial-app-data
  namespace: your-app-namespace
  labels:
    app: your-app-data
data:
  users.json: |
    {
      "admin": "admin123",
      "demo": "demo"
    }
  progress.json: |
    {}
  flashcard_progress.json: |
    {}

---
# PersistentVolume for data storage
apiVersion: v1
kind: PersistentVolume
metadata:
  name: your-app-data-pv
  labels:
    app: your-app
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  hostPath:
    path: /home/k8server/YourAppData  # Change to your path

---
# PersistentVolumeClaim
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: your-app-data-pvc
  namespace: your-app-namespace
  labels:
    app: your-app
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-storage
  resources:
    requests:
      storage: 5Gi

---
# One-time data initialization job
apiVersion: batch/v1
kind: Job
metadata:
  name: initialize-app-data
  namespace: your-app-namespace
  labels:
    app: your-app-data
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: data-initializer
        image: alpine:latest
        command: ['/bin/sh', '-c']
        args:
          - |
            echo "=== Initializing Application Data ==="
            
            # Only initialize if .data-initialized doesn't exist
            if [ -f "/data/.data-initialized" ]; then
              echo "✅ Data already initialized - preserving user data"
              echo "Files in persistent storage:"
              ls -la /data/*.json 2>/dev/null || echo "No JSON files found"
              exit 0
            fi
            
            echo "🔄 First time setup - copying default data"
            
            # Copy default data from ConfigMap if needed
            cp /config-data/* /data/ 2>/dev/null || echo "No config data to copy"
            
            # Create initialization marker
            touch /data/.data-initialized
            echo "$(date): Data initialized" > /data/.data-initialized
            
            echo "✅ Data initialization complete"
            ls -la /data/
        volumeMounts:
        - name: persistent-data
          mountPath: /data
        - name: config-data
          mountPath: /config-data
      volumes:
      - name: persistent-data
        persistentVolumeClaim:
          claimName: your-app-data-pvc
      - name: config-data
        configMap:
          name: initial-app-data
```

### Step 2: Create Application Deployment

**File: `k8s/deployment.yaml`**

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: your-app-namespace
  labels:
    app: your-app

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: your-app-config
  namespace: your-app-namespace
  labels:
    app: your-app
data:
  FLASK_ENV: "production"
  FLASK_APP: "main.py"
  DATA_PATH: "/app/data"

---
# Application Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: your-app
  namespace: your-app-namespace
  labels:
    app: your-app
    version: v1
  annotations:
    deployment.kubernetes.io/revision: "1"
    app.kubernetes.io/deployed-at: "2025-01-01T00:00:00Z"
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: your-app
  template:
    metadata:
      labels:
        app: your-app
        version: v1
    spec:
      # Init container - copy files to persistent storage
      initContainers:
      - name: setup-data
        image: your-dockerhub-username/your-app:latest
        command: ['/bin/sh', '-c']
        args:
          - |
            echo "=== Setting up persistent data ==="
            
            # Copy files to persistent storage ONLY if they don't exist  
            for file in users.json questions.json flashcards.json progress.json flashcard_progress.json; do
              if [ ! -f "/persistent-data/$file" ]; then
                echo "Copying default $file to persistent storage"
                cp -v "/app/$file" "/persistent-data/"
              else
                echo "Preserving existing $file in persistent storage"
              fi
            done
            
            echo "=== Files in persistent storage ==="
            ls -la /persistent-data/
        volumeMounts:
        - name: persistent-data
          mountPath: /persistent-data
      containers:
      - name: flask-app
        image: your-dockerhub-username/your-app:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 5019  # Change to your app's port
          name: http
          protocol: TCP
        env:
        - name: FLASK_ENV
          valueFrom:
            configMapKeyRef:
              name: your-app-config
              key: FLASK_ENV
        - name: FLASK_APP
          valueFrom:
            configMapKeyRef:
              name: your-app-config
              key: FLASK_APP
        - name: DATA_PATH
          valueFrom:
            configMapKeyRef:
              name: your-app-config
              key: DATA_PATH
        # Mount each JSON file directly from persistent storage
        volumeMounts:
        - name: persistent-data
          mountPath: /app/users.json
          subPath: users.json
        - name: persistent-data
          mountPath: /app/questions.json
          subPath: questions.json
        - name: persistent-data
          mountPath: /app/flashcards.json
          subPath: flashcards.json
        - name: persistent-data
          mountPath: /app/progress.json
          subPath: progress.json
        - name: persistent-data
          mountPath: /app/flashcard_progress.json
          subPath: flashcard_progress.json
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        # Health checks
        livenessProbe:
          httpGet:
            path: /
            port: 5019
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 5019
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      volumes:
      - name: persistent-data
        persistentVolumeClaim:
          claimName: your-app-data-pvc

---
# Service with MetalLB LoadBalancer
apiVersion: v1
kind: Service
metadata:
  name: your-app-service
  namespace: your-app-namespace
  labels:
    app: your-app
  annotations:
    metallb.universe.tf/loadBalancerIPs: 192.168.1.214  # Change to your IP
spec:
  type: LoadBalancer
  loadBalancerIP: 192.168.1.214  # Change to your IP
  selector:
    app: your-app
  ports:
  - name: http
    port: 80
    targetPort: 5019
    protocol: TCP
```

### Step 3: Deploy Data Setup (One-Time Only)

```bash
# Create the persistent storage directory
sudo mkdir -p /home/k8server/YourAppData
sudo chown k8server:k8server /home/k8server/YourAppData

# Deploy the data setup (run this only once)
kubectl apply -f k8s/data-setup.yaml

# Check the initialization job
kubectl get jobs -n your-app-namespace
kubectl logs job/initialize-app-data -n your-app-namespace

# Verify persistent volume is bound
kubectl get pv,pvc -n your-app-namespace
```

---

## Jenkins CI Pipeline

### Step 1: Set Up Credentials in Jenkins

**DockerHub Credentials:**
1. **Jenkins** → **Manage Jenkins** → **Manage Credentials**
2. **System** → **Global credentials** → **Add Credentials**
3. **Kind**: Username with password
4. **Username**: Your DockerHub username
5. **Password**: Your DockerHub password
6. **ID**: `dockerhub-credentials`
7. **Save**

**GitHub Credentials (for private repos):**
1. **Add Credentials** → **Username with password**
2. **Username**: Your GitHub username
3. **Password**: GitHub Personal Access Token
4. **ID**: `github-credentials`
5. **Save**

### Step 2: Create Jenkinsfile

**File: `Jenkinsfile`**

```groovy
pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_REPO = 'your-dockerhub-username/your-app'  // Change this
        IMAGE_TAG = "${BUILD_NUMBER}"
        GIT_REPO = 'https://github.com/your-username/your-repo.git'  // Change this
        GITHUB_CREDENTIALS = credentials('github-credentials')  // Only for private repos
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_HASH = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                    echo "Building commit: ${env.GIT_COMMIT_HASH}"
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${DOCKERHUB_REPO}:latest"
                    sh "docker build -t ${DOCKERHUB_REPO}:latest ."
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                script {
                    sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                    sh "docker push ${DOCKERHUB_REPO}:latest"
                    echo "Successfully pushed: ${DOCKERHUB_REPO}:latest"
                }
            }
        }
        
        stage('Trigger ArgoCD Deployment') {
            steps {
                script {
                    echo "✅ Image pushed as 'latest'"
                    echo "📝 ArgoCD will detect changes and deploy automatically"
                    echo "🔄 To trigger immediate deployment:"
                    echo "   Option 1: ArgoCD UI → Refresh → Sync"
                    echo "   Option 2: kubectl rollout restart deployment/your-app -n your-app-namespace"
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                expression { params.DIRECT_DEPLOY == true }
            }
            steps {
                script {
                    try {
                        echo "Direct deployment requested..."
                        sh 'kubectl rollout restart deployment/your-app -n your-app-namespace'
                        sh 'kubectl rollout status deployment/your-app -n your-app-namespace --timeout=300s'
                        echo "✅ Direct deployment successful!"
                    } catch (Exception e) {
                        echo "⚠️  Direct deployment failed - ArgoCD will handle it"
                    }
                }
            }
        }
    }
    
    post {
        always {
            sh """
                docker rmi ${DOCKERHUB_REPO}:latest || true
                docker system prune -f
            """
        }
        success {
            echo "✅ CI Pipeline completed successfully!"
            echo "🚀 Image built and pushed: ${DOCKERHUB_REPO}:latest"
            echo ""
            echo "🔄 To deploy the new image:"
            echo "   Option 1: ArgoCD UI → Refresh → Sync"
            echo "   Option 2: kubectl rollout restart deployment/your-app -n your-app-namespace"
            echo ""
            echo "🌐 App will be available at: http://YOUR_LOAD_BALANCER_IP"
        }
        failure {
            echo "❌ Pipeline failed!"
            echo "🔍 Check which stage failed above"
            echo "💡 Common issues: Docker build, DockerHub push, or kubectl access"
        }
    }
}
```

### Step 3: Create Jenkins Pipeline Job

1. **Jenkins Dashboard** → **New Item**
2. **Item name**: `your-app-pipeline`
3. **Type**: Pipeline
4. **Pipeline Definition**: Pipeline script from SCM
5. **SCM**: Git
6. **Repository URL**: Your Git repository URL
7. **Credentials**: Select GitHub credentials (if private repo)
8. **Branch**: `*/main`
9. **Script Path**: `Jenkinsfile`
10. **Save**

---

## ArgoCD Configuration

### Step 1: Access ArgoCD UI

```bash
# Get ArgoCD admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo

# Access ArgoCD UI (adjust URL/port as needed)
# http://your-argocd-url:port
```

### Step 2: Add Repository (If Private)

**For private repositories:**

1. **Settings** → **Repositories** → **CONNECT REPO**
2. **Choose connection method**: HTTPS
3. **Type**: git
4. **Repository URL**: `https://github.com/your-username/your-repo.git`
5. **Username**: Your GitHub username
6. **Password**: GitHub Personal Access Token
7. **Connect**

### Step 3: Create ArgoCD Application

**Method A: Using UI**

1. **Applications** → **NEW APP**
2. **Application Name**: `your-app`
3. **Project**: `default`
4. **Source**:
   - **Repository URL**: Your Git repository URL
   - **Revision**: `main`
   - **Path**: `k8s`
5. **Destination**:
   - **Cluster URL**: `https://kubernetes.default.svc`
   - **Namespace**: `your-app-namespace`
6. **Sync Policy**: 
   - **Policy**: Automatic
   - **Options**: 
     - ✅ PRUNE RESOURCES
     - ✅ SELF HEAL
7. **Create**

**Method B: Using YAML**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: your-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-username/your-repo.git
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: your-app-namespace
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

```bash
kubectl apply -f argocd-application.yaml
```

---

## GitHub Integration

### Option 1: GitHub Webhooks (Instant Builds - Recommended)

**Step 1: Configure Jenkins**
1. **Pipeline** → **Configure** → **Build Triggers**
2. ✅ **GitHub hook trigger for GITScm polling**
3. **Save**

**Step 2: Configure GitHub Webhook**
1. **GitHub Repository** → **Settings** → **Webhooks**
2. **Add webhook**
3. **Payload URL**: `https://your-jenkins-domain/github-webhook/`
4. **Content type**: `application/json`
5. **Which events**: Just the push event
6. **Active**: ✅
7. **Add webhook**

### Option 2: SCM Polling (Simple Alternative)

**Configure Jenkins only:**
1. **Pipeline** → **Configure** → **Build Triggers**
2. ✅ **Poll SCM**
3. **Schedule**: `H/5 * * * *` (every 5 minutes)
4. **Save**

---

## Complete GitOps Workflow

### Initial Setup Workflow

```bash
# 1. Create persistent storage directory
sudo mkdir -p /home/k8server/YourAppData
sudo chown k8server:k8server /home/k8server/YourAppData

# 2. Deploy data setup (one-time)
kubectl apply -f k8s/data-setup.yaml

# 3. Verify data initialization
kubectl get jobs -n your-app-namespace
kubectl logs job/initialize-app-data -n your-app-namespace

# 4. Initial application deployment
kubectl apply -f k8s/deployment.yaml

# 5. Verify application is running
kubectl get pods,svc -n your-app-namespace

# 6. Test application access
curl http://YOUR_LOAD_BALANCER_IP
```

### Development Workflow

```
1. Code Changes
   ↓
2. git add/commit/push
   ↓
3. GitHub Webhook → Jenkins (immediate)
   ↓
4. Jenkins Pipeline:
   - Checkout code
   - Build Docker image
   - Push to DockerHub
   ↓
5. ArgoCD detects image change
   ↓
6. ArgoCD syncs and deploys
   ↓
7. Application updated! 🚀
```

### Typical Development Commands

```bash
# Make changes to your application
echo "// Update $(date)" >> main.py

# Commit and push
git add .
git commit -m "Update application feature"
git push origin main

# Jenkins automatically builds and pushes image
# ArgoCD automatically detects and deploys

# Monitor deployment
kubectl get pods -n your-app-namespace -w

# Check application logs
kubectl logs -f deployment/your-app -n your-app-namespace

# Access application
curl http://YOUR_LOAD_BALANCER_IP
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Docker Build Failures

**Issue**: `COPY questions.json .: no such file or directory`

**Solution**: Create minimal default JSON files
```bash
echo '{}' > users.json
echo '[]' > questions.json
echo '[]' > flashcards.json
echo '{}' > progress.json
echo '{}' > flashcard_progress.json
git add *.json && git commit -m "Add default data files" && git push
```

#### 2. Data Not Persisting

**Check persistent volume mounting:**
```bash
# Verify persistent volume is bound
kubectl get pv,pvc -n your-app-namespace

# Check if data directory exists
kubectl exec -it deployment/your-app -n your-app-namespace -- ls -la /app/

# Verify files are mounted from persistent storage
kubectl exec -it deployment/your-app -n your-app-namespace -- ls -la /app/*.json

# Check persistent storage on host
ls -la /home/k8server/YourAppData/
```

#### 3. Jenkins Build Not Triggering

**For Webhooks:**
```bash
# Test webhook URL
curl -X POST https://your-jenkins-domain/github-webhook/

# Check GitHub webhook deliveries
# GitHub → Settings → Webhooks → Recent Deliveries
```

**For Polling:**
```bash
# Check Jenkins polling logs
# Jenkins → Your Pipeline → Configure → Build Triggers
# Verify "Poll SCM" is enabled with correct schedule
```

#### 4. ArgoCD Sync Issues

**Check ArgoCD application status:**
```bash
# CLI method
kubectl get applications -n argocd

# Or via ArgoCD UI
# Check for "Out of Sync" or "Failed" status
```

**Common ArgoCD fixes:**
```bash
# Manual sync
argocd app sync your-app

# Refresh application
argocd app get your-app --refresh

# Check repository access
argocd repo list
```

#### 5. Pod CrashLoopBackOff

**Debug pod issues:**
```bash
# Check pod status
kubectl get pods -n your-app-namespace

# Check pod logs
kubectl logs deployment/your-app -n your-app-namespace

# Check init container logs
kubectl logs deployment/your-app -n your-app-namespace -c setup-data

# Describe pod for more details
kubectl describe pod -l app=your-app -n your-app-namespace
```

### Debug Commands Reference

```bash
# Kubernetes debugging
kubectl get all -n your-app-namespace
kubectl describe deployment/your-app -n your-app-namespace
kubectl logs -f deployment/your-app -n your-app-namespace
kubectl exec -it deployment/your-app -n your-app-namespace -- /bin/sh

# Check persistent storage
ls -la /home/k8server/YourAppData/
df -h | grep YourAppData

# ArgoCD debugging
kubectl get applications -n argocd
kubectl describe application your-app -n argocd

# Jenkins debugging
# Check Jenkins build console output
# Check Jenkins system logs for webhook issues
```

---

## Maintenance & Updates

### Regular Maintenance Tasks

#### 1. Update Dependencies

```bash
# Update Python dependencies
pip list --outdated
# Update requirements.txt with new versions
# Commit and push changes

# Update base Docker image
# Change Dockerfile: FROM python:3.9-slim → python:3.10-slim
# Commit and push
```

#### 2. Monitor Resource Usage

```bash
# Check pod resource usage
kubectl top pods -n your-app-namespace

# Check persistent volume usage
kubectl exec -it deployment/your-app -n your-app-namespace -- df -h

# Monitor application logs
kubectl logs -f deployment/your-app -n your-app-namespace
```

#### 3. Backup Data

```bash
# Backup persistent data
sudo tar -czf app-data-backup-$(date +%Y%m%d).tar.gz /home/k8server/YourAppData/

# Backup Kubernetes manifests
tar -czf k8s-manifests-backup-$(date +%Y%m%d).tar.gz k8s/
```

#### 4. Security Updates

```bash
# Update Docker base image regularly
# Scan images for vulnerabilities (if using tools like Trivy)
# Update Kubernetes cluster
# Update Jenkins plugins
# Rotate GitHub Personal Access Tokens
# Rotate DockerHub passwords
```

### Scaling and Performance

#### Scale Application

```bash
# Scale pods horizontally
kubectl scale deployment/your-app --replicas=5 -n your-app-namespace

# Update in deployment.yaml for persistence
# spec.replicas: 5
```

#### Add Resource Limits

```yaml
# In deployment.yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

#### Add Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: your-app-hpa
  namespace: your-app-namespace
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: your-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Advanced Features

#### Add Ingress (Alternative to LoadBalancer)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: your-app-ingress
  namespace: your-app-namespace
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: your-app.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: your-app-service
            port:
              number: 80
```

#### Add TLS/SSL

```yaml
# Add to ingress
spec:
  tls:
  - hosts:
    - your-app.yourdomain.com
    secretName: your-app-tls
```

#### Add Monitoring

```yaml
# Prometheus monitoring annotations
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "5019"
    prometheus.io/path: "/metrics"
```

---

## Reference Information

### Important URLs and Commands

```bash
# Application Access
http://YOUR_LOAD_BALANCER_IP        # Your application
https://jenkins.yourdomain.com      # Jenkins CI
https://argocd.yourdomain.com       # ArgoCD UI

# Quick Commands
kubectl get all -n your-app-namespace                    # Check all resources
kubectl logs -f deployment/your-app -n your-app-namespace # Check logs
kubectl rollout restart deployment/your-app -n your-app-namespace # Manual restart
kubectl get pv,pvc -n your-app-namespace                # Check storage

# Data Access
ls -la /home/k8server/YourAppData/                      # Check persistent data
kubectl exec -it deployment/your-app -n your-app-namespace -- ls -la /app/ # Check mounted files
```

### Default Values to Customize

When setting up your own application, change these values:

- `your-app-namespace` → Your preferred namespace
- `your-dockerhub-username/your-app` → Your DockerHub repository
- `https://github.com/your-username/your-repo.git` → Your Git repository
- `/home/k8server/YourAppData` → Your persistent storage path
- `192.168.1.214` → Your Load Balancer IP
- `5019` → Your application port
- `dockerhub-credentials` → Your Jenkins credential IDs
- `github-credentials` → Your Jenkins credential IDs

### Environment-Specific Configurations

#### Development Environment
- Use NodePort instead of LoadBalancer
- Enable debug logging
- Smaller resource requests
- Manual sync in ArgoCD

#### Production Environment
- Use proper domain with Ingress + TLS
- Enable automatic backups
- Set up monitoring and alerting
- Use secrets for sensitive data
- Enable resource quotas and limits
- Set up disaster recovery procedures

---

## Conclusion

This guide provides a complete, production-ready GitOps setup for Flask applications with:

- ✅ **Continuous Integration** with Jenkins
- ✅ **Continuous Deployment** with ArgoCD  
- ✅ **Data persistence** and separation
- ✅ **Automatic builds** on code changes
- ✅ **Container orchestration** with Kubernetes
- ✅ **Load balancing** with MetalLB
- ✅ **Proper security** practices

The setup ensures that:
- **Code changes trigger automatic builds and deployments**
- **User data is never lost during deployments**
- **Applications are highly available and scalable**
- **Infrastructure is managed as code**
- **DevOps processes are streamlined and reliable**

For support or questions, refer to the troubleshooting section or check the official documentation for each tool.

---

**Happy GitOps! 🚀**