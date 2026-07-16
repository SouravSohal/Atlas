#!/bin/bash
# ==============================================================================
# ATLAS FastAPI Backend Startup Script
#
# Target Database Engine: Cloud Firestore
# Target Database Name: atlas-01
# Target GCP Project: atlas-501808
# ==============================================================================

echo "----------------------------------------------------------------"
echo "🚀 Booting ATLAS Operational Intelligence Backend API Server..."
echo "📂 Target GCP Project: atlas-501808"
echo "🗄️ Target Firestore DB: atlas-01"
echo "----------------------------------------------------------------"

# Set up environment and python paths
export PYTHONPATH="services/api/src:packages/atlas-core/src"
export GOOGLE_CLOUD_PROJECT="atlas-501808"
export FIRESTORE_DATABASE="atlas-01"

# Boot Uvicorn
.venv/bin/python -m uvicorn services.api.src.app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
