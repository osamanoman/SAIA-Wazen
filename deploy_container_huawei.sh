#!/bin/bash

# SAIA Wazen Container Deployment Script for Huawei Cloud CCE
# This script builds and deploys the SAIA application to Huawei Cloud Container Engine

set -e  # Exit on any error

echo "🚀 Starting SAIA Wazen Container Deployment on Huawei Cloud..."

# Configuration - UPDATE THESE VALUES
HUAWEI_REGION="me-east-1"
SWR_REGISTRY="swr.${HUAWEI_REGION}.myhuaweicloud.com"
ORGANIZATION="wazen-containers"
IMAGE_NAME="saia-wazen-app"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${SWR_REGISTRY}/${ORGANIZATION}/${IMAGE_NAME}:${IMAGE_TAG}"
NAMESPACE="saia-wazen"
DOMAIN="your-domain.com"  # Change this to your actual domain

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

print_status "Prerequisites check passed!"

# Step 1: Build Docker image
print_step "Building Docker image..."
docker build -t $FULL_IMAGE_NAME .

if [ $? -eq 0 ]; then
    print_status "Docker image built successfully: $FULL_IMAGE_NAME"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Step 2: Login to Huawei SWR (Software Repository for Container)
print_step "Logging into Huawei SWR..."
print_warning "Please make sure you have configured Huawei Cloud CLI credentials"
print_warning "Run: huaweicloud configure set --profile=default --cli-region=$HUAWEI_REGION"

# You'll need to login to SWR - this requires Huawei Cloud credentials
echo "Please login to Huawei SWR manually:"
echo "docker login -u ${HUAWEI_REGION}@[YOUR_AK] -p [YOUR_LOGIN_KEY] ${SWR_REGISTRY}"
echo "Press Enter after you've logged in..."
read -p ""

# Step 3: Push image to Huawei SWR
print_step "Pushing image to Huawei SWR..."
docker push $FULL_IMAGE_NAME

if [ $? -eq 0 ]; then
    print_status "Image pushed successfully to Huawei SWR"
else
    print_error "Failed to push image to SWR"
    exit 1
fi

# Step 4: Update Kubernetes manifests with correct image name
print_step "Updating Kubernetes manifests..."
sed -i "s|swr.me-east-1.myhuaweicloud.com/wazen-containers/saia-wazen-app:latest|$FULL_IMAGE_NAME|g" k8s/saia-deployment.yaml
sed -i "s|your-domain.com|$DOMAIN|g" k8s/saia-deployment.yaml k8s/ingress.yaml

print_status "Kubernetes manifests updated"

# Step 5: Deploy to Kubernetes
print_step "Deploying to Kubernetes cluster..."

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml

# Deploy databases
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml

# Wait for databases to be ready
print_status "Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=saia-postgres -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=wazen-mysql -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=saia-redis -n $NAMESPACE --timeout=300s

# Deploy application
kubectl apply -f k8s/saia-deployment.yaml

# Wait for application to be ready
print_status "Waiting for application to be ready..."
kubectl wait --for=condition=ready pod -l app=saia-app -n $NAMESPACE --timeout=600s

# Apply ingress and HPA
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

print_status "✅ SAIA Wazen container deployment completed successfully!"

# Step 6: Display deployment information
print_step "Deployment Information:"
echo "=================================="
echo "Namespace: $NAMESPACE"
echo "Image: $FULL_IMAGE_NAME"
echo "Domain: $DOMAIN"
echo ""

# Get service information
print_status "Getting service information..."
kubectl get services -n $NAMESPACE
echo ""

# Get pod information
print_status "Getting pod information..."
kubectl get pods -n $NAMESPACE
echo ""

# Get ingress information
print_status "Getting ingress information..."
kubectl get ingress -n $NAMESPACE

print_warning "⚠️  Important Next Steps:"
print_warning "   1. Update DNS records to point $DOMAIN to your load balancer IP"
print_warning "   2. Configure SSL certificates (update k8s/ingress.yaml)"
print_warning "   3. Update secrets in k8s/secrets.yaml with real values"
print_warning "   4. Configure monitoring and logging"
print_warning "   5. Set up database backups"
print_warning "   6. Test the widget API: https://$DOMAIN/api/widget/config/wazen/"

echo ""
print_status "🎉 Container deployment completed!"
print_status "📊 Monitor your deployment with: kubectl get all -n $NAMESPACE"
print_status "📝 View logs with: kubectl logs -f deployment/saia-app -n $NAMESPACE"
