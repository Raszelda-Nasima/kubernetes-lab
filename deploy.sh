#!/bin/bash
# Kubernetes Lab Deployment Script

set -e  # Exit on error

echo "====================================="
echo "Kubernetes Lab Deployment Script"
echo "====================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "ERROR: kubectl is not installed or not in PATH"
    exit 1
fi

# Check cluster connectivity
echo ""
echo "Checking Kubernetes cluster..."
if kubectl cluster-info &> /dev/null; then
    echo "✓ Kubernetes cluster is accessible"
else
    echo "ERROR: Cannot connect to Kubernetes cluster"
    echo "Make sure Docker Desktop Kubernetes is enabled"
    exit 1
fi

# Create namespace
echo ""
echo "Creating namespace..."
kubectl apply -f namespace.yaml
echo "✓ Namespace created"

# Apply ConfigMaps and Secrets
echo ""
echo "Applying configuration..."
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f nginx-configmap.yaml
echo "✓ Configuration applied"

# Create storage
echo ""
echo "Creating persistent storage..."
kubectl apply -f postgres-pvc.yaml
echo "✓ Storage created"

# Deploy PostgreSQL
echo ""
echo "Deploying PostgreSQL..."
kubectl apply -f postgres-deployment.yaml
kubectl apply -f postgres-service.yaml
echo "✓ PostgreSQL deployed"

# Wait for PostgreSQL to be ready
echo ""
echo "Waiting for PostgreSQL to be ready (this may take 1-2 minutes)..."
kubectl wait --for=condition=ready pod -l app=postgres -n app-production --timeout=300s 2>/dev/null || {
    echo "⚠ PostgreSQL pod is taking longer to start, continuing..."
}

# Deploy Nginx
echo ""
echo "Deploying Nginx..."
kubectl apply -f nginx-deployment.yaml
kubectl apply -f nginx-service.yaml
echo "✓ Nginx deployed"

# Wait for Nginx to be ready
echo ""
echo "Waiting for Nginx to be ready..."
kubectl wait --for=condition=ready pod -l app=nginx -n app-production --timeout=60s 2>/dev/null || {
    echo "⚠ Nginx pods are starting up..."
}

# Display deployment status
echo ""
echo "====================================="
echo "Deployment Status"
echo "====================================="
echo ""
echo "Namespaces:"
kubectl get namespace app-production

echo ""
echo "Deployments:"
kubectl get deployments -n app-production

echo ""
echo "Pods:"
kubectl get pods -n app-production

echo ""
echo "Services:"
kubectl get services -n app-production

echo ""
echo "====================================="
echo "✓ Deployment Complete!"
echo "====================================="
echo ""
echo "Access the application:"
echo "  Nginx: http://localhost:80"
echo "  Health check: http://localhost:80/health"
echo "  DB info: http://localhost:80/db-info"
echo ""
echo "Connect to PostgreSQL:"
kubectl get pods -n app-production -l app=postgres -o jsonpath='{.items[0].metadata.name}' | xargs -I {} echo "  kubectl exec -it {} -n app-production -- psql -U appuser -d appdb"
echo ""
echo "View logs:"
echo "  kubectl logs -f deployment/nginx -n app-production"
echo "  kubectl logs -f deployment/postgres -n app-production"
echo ""
