# GitOps Learning Repository

Welcome to the GitOps Learning Repository! This repository serves as a sandbox for learning and experimenting with GitOps practices using a variety of tools like Jenkins, ArgoCD, and more. Here, we aim to cover the essentials of GitOps, continuous integration (CI), and continuous deployment (CD) workflows by setting up sample pipelines and deployments.

## 📊 Interactive Architecture Overview

Explore the complete repository architecture and learning path with our interactive diagram:

**[🚀 View GitOps Learning Repository Architecture](https://sohaib1khan.github.io/GitOps_Projects/)**

## Table of Contents

- [GitOps Learning Repository](#gitops-learning-repository)
  - [📊 Interactive Architecture Overview](#-interactive-architecture-overview)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [What is GitOps?](#what-is-gitops)
  - [Tools Covered](#tools-covered)
  - [Repository Structure](#repository-structure)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
  - [Examples](#examples)
    - [ArgoCD](#argocd)
    - [Jenkins](#jenkins)
    - [Future Tools](#future-tools)
  - [Resources](#resources)

## Overview

This repository is intended to be a practical guide for anyone looking to understand and implement GitOps practices. We will use tools that align with the principles of GitOps, enabling us to manage our infrastructure and applications declaratively and with version control.

## What is GitOps?

GitOps is a set of practices that uses Git as a source of truth for declarative infrastructure and applications. GitOps allows for automation, reproducibility, and visibility in managing Kubernetes and cloud-native applications by leveraging Git workflows.

## Tools Covered

This repository will cover several tools commonly used in GitOps workflows. Each tool will have its own dedicated section with sample configurations and example use cases. Tools include:

- **[ArgoCD](https://argo-cd.readthedocs.io/)**: A declarative, GitOps continuous delivery tool for Kubernetes.
- **[Jenkins](https://www.jenkins.io/)**: An open-source automation server that supports building, deploying, and automating CI/CD pipelines.
- Additional tools and examples will be added over time.

## Repository Structure
```
├── argocd/                # ArgoCD configuration and example manifests
│   ├── README.md          # Overview and instructions specific to ArgoCD
│   └── sample-app/        # Example applications for ArgoCD deployments
├── jenkins/               # Jenkins pipeline and configuration examples
│   ├── README.md          # Overview and instructions specific to Jenkins
│   └── pipelines/         # Sample Jenkins pipelines for GitOps
└── README.md              # Main repository README (this file)
```
## Getting Started

To start learning GitOps with this repository, clone it to your local machine:

```
git clone https://github.com/yourusername/gitops-learning.git
cd gitops-learning

```

### Prerequisites

Before using the examples in this repository, ensure you have:

- A Kubernetes cluster (e.g., k3s, minikube) with `kubectl` configured.
- Helm (for tools like ArgoCD).
- ArgoCD or Jenkins installed (instructions provided in each tool's section).

## Examples

### ArgoCD

ArgoCD is a GitOps tool designed for Kubernetes. It continuously monitors Git repositories and keeps Kubernetes clusters in sync with declarative configurations.

- **Getting Started**: Instructions to install ArgoCD on a Kubernetes cluster.
- **Sample Applications**: Configuration files for deploying sample applications using ArgoCD.
- **Sync Policies and Automation**: Examples of automated syncing and rollback scenarios.

For more details, visit the ArgoCD directory.

### Jenkins

Jenkins is a popular CI/CD tool used to automate building, testing, and deploying applications.

- **GitOps with Jenkins**: Using Jenkins to trigger Kubernetes deployments based on Git changes.
- **Pipeline Examples**: Sample Jenkinsfiles for automating CI/CD workflows.
- **Integrations**: Using Jenkins in conjunction with ArgoCD to achieve full GitOps workflows.

For more details, visit the Jenkins directory.

### Future Tools

As this repository grows, we will add examples and configurations for other tools, such as:

- **FluxCD**: Another popular GitOps tool for Kubernetes.
- **Tekton**: A Kubernetes-native framework for creating CI/CD pipelines.
- **Prometheus and Grafana**: For monitoring GitOps workflows.

## Resources

- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [GitOps Principles](https://www.gitops.tech/)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
