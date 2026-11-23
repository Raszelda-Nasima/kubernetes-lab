# Kubernetes Lab: Multi-Tier Application Deployment

## Project Overview

This lab demonstrates **production-ready Kubernetes deployment** concepts using Docker Desktop's built-in Kubernetes cluster. It shows how to orchestrate a multi-tier application with:
- **Frontend**: Nginx web server (3 replicas for redundancy)
- **Backend Database**: PostgreSQL with persistent storage
- **Configuration Management**: Kubernetes ConfigMaps and Secrets
- **Networking**: Service discovery and load balancing
- **Storage**: Persistent volumes for data persistence
- **Health Monitoring**: Liveness and readiness probes

---

## Architecture Components

### 1. **Namespace** (`namespace.yaml`)
**What it does:** Organizes resources into isolated virtual clusters within Kubernetes
- Allows multiple teams/projects to coexist without interfering
- Provides resource quotas and access control boundaries
- Our lab uses `app-production` namespace to simulate production environment

**Why it matters:** Shows understanding of multi-tenancy and resource organization in enterprise Kubernetes

---

### 2. **ConfigMap** (`configmap.yaml` & `nginx-configmap.yaml`)
**What it does:** Stores non-sensitive configuration data as key-value pairs
- Decouples configuration from container images
- Allows configuration changes without rebuilding containers
- Used by both PostgreSQL and Nginx services

**Example data:**
```
POSTGRES_USER: appuser
POSTGRES_DB: appdb
LOG_LEVEL: INFO
```

**Why it matters:** Demonstrates DevOps principle of separating config from code, enabling CI/CD workflows

---

### 3. **Secret** (`secret.yaml`)
**What it does:** Stores sensitive data (passwords, API keys, database credentials)
- Base64-encoded to prevent casual reading (not encrypted by default)
- In production, use HashiCorp Vault or cloud provider's secret manager
- Can be referenced by pods via environment variables or volume mounts

---

### 4. **PersistentVolumeClaim (PVC)** (`postgres-pvc.yaml`)
**What it does:** Requests storage from Kubernetes cluster
- Without PVC: Container data is lost when pod restarts (ephemeral)
- With PVC: Data persists across pod restarts and recreation
- Kubernetes abstracts underlying storage (local disk, cloud storage, NFS, etc.)

**How it works:**
```
Container → PVC → PersistentVolume → Physical Storage
```

**Why it matters:** Essential for stateful applications (databases, file servers) that need data durability

---

### 5. **PostgreSQL Deployment** (`postgres-deployment.yaml`)
**What it does:** Declaratively manages PostgreSQL database pods
- Ensures specified number of replicas always running
- Automatically restarts failed pods
- Manages rolling updates without downtime

**Key features:**
- **Replicas: 1** - Single PostgreSQL instance (can scale to multiple for clustering)
- **Volume Mounts** - Connects to persistent storage for data
- **Resource Limits** - Prevents pod from consuming excessive cluster resources
- **Liveness Probe** - Restarts container if it becomes unhealthy
- **Readiness Probe** - Removes unhealthy pod from service traffic

**Why it matters:** Demonstrates high-availability patterns and self-healing infrastructure

---

### 6. **PostgreSQL Service** (`postgres-service.yaml`)
**What it does:** Exposes PostgreSQL pod to other pods in cluster
- Provides stable DNS name: `postgres-service.app-production.svc.cluster.local`
- Routes traffic to any healthy PostgreSQL pod
- **ClusterIP type** - Internal only (accessible only from within cluster)

**Service Discovery Flow:**
```
Nginx Pod → Requests "postgres-service" → Kubernetes DNS → Routes to PostgreSQL Pod
```

**Why it matters:** Demonstrates service mesh concepts and container networking

---

### 7. **Nginx Deployment** (`nginx-deployment.yaml`)
**What it does:** Runs web server instances for high availability
- **3 replicas** - Kubernetes automatically load-balances traffic
- Each instance can independently fail without breaking application
- Kubernetes reschedules failed pods on healthy nodes

**Key features:**
- Mounts configuration from ConfigMap
- Uses resources limits for fair cluster resource sharing
- Health probes ensure only healthy pods receive traffic

**Why it matters:** Shows understanding of horizontal scaling and fault tolerance

---

### 8. **Nginx Service** (`nginx-service.yaml`)
**What it does:** Exposes Nginx to outside the cluster
- **LoadBalancer type** - In Docker Desktop, forwards to localhost
- In cloud (AWS/OpenShift), provisions actual load balancer
- Distributes traffic across all 3 Nginx replicas

**Access from host machine:**
```
http://localhost:80 → Kubernetes Service → Load Balancer → One of 3 Nginx Pods
```

**Why it matters:** Demonstrates ingress patterns and external traffic routing

---

## Deployment Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   Docker Desktop                             │
│        (Kubernetes Cluster with 1 Master + Worker)          │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
      ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
      │   Nginx-1   │ │   Nginx-2   │ │   Nginx-3   │
      │  Container  │ │  Container  │ │  Container  │
      │ Port: 80    │ │ Port: 80    │ │ Port: 80    │
      └──────▲──────┘ └──────▲──────┘ └──────▲──────┘
             │               │               │
             └───────────────┼───────────────┘
                             │
                  ┌──────────▼──────────┐
                  │  Nginx Service      │
                  │  (LoadBalancer)     │
                  │  Port: 80           │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │   localhost:80      │
                  │   (Host Machine)    │
                  └─────────────────────┘

              ┌────────────────────────┐
              │  PostgreSQL Pod        │
              │  ┌──────────────────┐  │
              │  │   Postgres 16    │  │
              │  │   Port: 5432     │  │
              │  └────────┬─────────┘  │
              │           │            │
              │  ┌────────▼─────────┐  │
              │  │  Persistent Vol  │  │
              │  │  5GB Storage     │  │
              │  └──────────────────┘  │
              └────────────────────────┘
                        ▲
                        │
              ┌─────────▼─────────┐
              │ Postgres Service  │
              │ (ClusterIP)       │
              │ postgres-service  │
              └───────────────────┘
                        │
           ┌────────────┘
           │
      (Nginx connects to PostgreSQL via service name)
```

---

## Key Kubernetes Concepts Demonstrated

### 1. **Declarative vs Imperative**
- We declare **what** we want (via YAML files)
- Kubernetes figures out **how** to achieve it
- Shows difference from traditional VM management

### 2. **Self-Healing**
- Deployment continuously monitors pod health
- Unhealthy pods are automatically replaced
- Shows automatic recovery pattern

### 3. **Scaling**
- Change `replicas: 3` to `replicas: 5` to scale Nginx up
- Kubernetes automatically creates/destroys pods as needed
- Demonstrates horizontal scaling (more pods) vs vertical (more CPU/RAM)

### 4. **Configuration Management**
- ConfigMaps for non-sensitive config
- Secrets for sensitive data
- Shows separation of concerns principle

### 5. **Networking**
- Services provide service discovery (DNS names)
- Pods communicate using service names, not IPs
- ClusterIP (internal) vs LoadBalancer (external) types

### 6. **Storage**
- PersistentVolumeClaim requests storage without caring about underlying implementation
- Demonstrates abstraction layer in Kubernetes

### 7. **Resource Management**
- Resource requests (minimum needed)
- Resource limits (maximum allowed)
- Kubernetes uses these for scheduling and cluster optimization

---

## Deployment Instructions

### Prerequisites
- Docker Desktop with Kubernetes enabled
- kubectl CLI tool (bundled with Docker Desktop)

### Step 1: Enable Kubernetes in Docker Desktop
1. Open Docker Desktop
2. Settings → Kubernetes → Check "Enable Kubernetes"
3. Click "Apply & Restart"
4. Wait 2-3 minutes for cluster to be ready

### Step 2: Verify Kubernetes Cluster
```bash
kubectl get nodes
# Should show 1 node (docker-desktop)

kubectl get namespaces
# Should show default system namespaces
```

### Step 3: Deploy the Application
```bash
# Create all resources in correct order
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f postgres-pvc.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml
kubectl apply -f nginx-configmap.yaml
kubectl apply -f nginx-deployment.yaml
kubectl apply -f nginx-service.yaml

# Or apply all at once:
kubectl apply -f .
```

### Step 4: Monitor Deployment
```bash
# Watch pods starting up
kubectl get pods -n app-production -w

# Check deployment status
kubectl get deployments -n app-production

# View service details
kubectl get svc -n app-production
```

### Step 5: Access the Application
```bash
# Get service details
kubectl get svc nginx-service -n app-production

# Visit in browser
http://localhost:80

# Check health endpoint
http://localhost:80/health

# View database connection info
http://localhost:80/db-info
```

### Step 6: Verify Database Connectivity
```bash
# Get PostgreSQL pod name
kubectl get pods -n app-production -l app=postgres

# Connect to PostgreSQL
kubectl exec -it <postgres-pod-name> -n app-production -- psql -U appuser -d appdb

# Inside psql prompt, verify it's working:
\dt  # List tables
\q   # Quit
```

---

## Troubleshooting Commands

```bash
# Check pod status
kubectl describe pod <pod-name> -n app-production

# View pod logs
kubectl logs <pod-name> -n app-production

# Access pod shell
kubectl exec -it <pod-name> -n app-production -- /bin/bash

# Port forward to access service locally
kubectl port-forward svc/postgres-service 5432:5432 -n app-production

# Delete deployment and start over
kubectl delete namespace app-production
```

---

## Scaling Exercises

### Scale Nginx up to 5 replicas:
```bash
kubectl scale deployment nginx --replicas=5 -n app-production
kubectl get pods -n app-production  # Watch new pods appear
```

### Scale back down:
```bash
kubectl scale deployment nginx --replicas=2 -n app-production
```

---

## Production Enhancements

This lab demonstrates core concepts. For production, add:
1. **Network Policies** - Restrict pod-to-pod communication
2. **RBAC** - Role-based access control
3. **Pod Security Policies** - Enforce security standards
4. **Ingress** - Advanced HTTP routing
5. **HPA** - Horizontal Pod Autoscaler (auto-scale based on CPU usage)
6. **Monitoring** - Prometheus + Grafana for metrics
7. **Logging** - ELK stack for centralized logs
8. **Service Mesh** - Istio for advanced traffic management
9. **GitOps** - ArgoCD for declarative deployment

---

## Why This Matters for Your CV

This project demonstrates:
- ✅ **Kubernetes & OpenShift understanding** (core orchestration platform)
- ✅ **Linux system administration** (container orchestration, networking, storage)
- ✅ **Configuration management** (ConfigMaps, Secrets, declarative IaC)
- ✅ **High availability patterns** (redundancy, self-healing, load balancing)
- ✅ **Production mindset** (resource limits, health probes, persistent storage)
- ✅ **DevOps practices** (infrastructure as code, service discovery, monitoring)


---

## References

- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [Docker Desktop Kubernetes](https://docs.docker.com/desktop/kubernetes/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
