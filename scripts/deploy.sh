#!/bin/bash
# VeriClip AI - Deployment Script
# Deploys backend to Cloud Run and frontend to Firebase Hosting

set -e

echo "=========================================="
echo "  VeriClip AI - Deploy to Production"
echo "=========================================="

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-vericlip-ai-2026}
REGION=${GCP_REGION:-asia-south1}
IMAGE_NAME="vericlip-api"
IMAGE_TAG="${IMAGE_NAME}:$(git rev-parse --short HEAD)"

# Check prerequisites
echo "Checking prerequisites..."
command -v gcloud >/dev/null 2>&1 || { echo "gcloud CLI not found"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker not found"; exit 1; }

# Authenticate
echo "Authenticating to Google Cloud..."
gcloud auth configure-docker

# Build and push backend
echo ""
echo "▶ Building Docker image..."
docker build -t gcr.io/${PROJECT_ID}/${IMAGE_TAG} .

echo ""
echo "▶ Pushing image to GCR..."
docker push gcr.io/${PROJECT_ID}/${IMAGE_TAG}

# Deploy to Cloud Run
echo ""
echo "▶ Deploying to Cloud Run..."
gcloud run deploy vericlip-api \
    --image gcr.io/${PROJECT_ID}/${IMAGE_TAG} \
    --region ${REGION} \
    --allow-unauthenticated \
    --min-instances 2 \
    --max-instances 10 \
    --memory 512Mi \
    --timeout 30s

# Get service URL
SERVICE_URL=$(gcloud run services describe vericlip-api --region ${REGION} --format 'value(status.url)')
echo ""
echo "✓ Backend deployed: ${SERVICE_URL}"

# Deploy frontend to Firebase (if available)
if command -v firebase >/dev/null 2>&1 && [ -d "frontend" ]; then
    echo ""
    echo "▶ Deploying frontend to Firebase Hosting..."
    cd frontend
    flutter build web || echo "Flutter build failed, skipping frontend"
    firebase deploy --only hosting
    echo "✓ Frontend deployed"
    cd ..
fi

echo ""
echo "=========================================="
echo "  Deployment complete! 🚀"
echo "  Backend: ${SERVICE_URL}/api/v1/health"
echo "=========================================="
