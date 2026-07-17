# ==============================================================================
# Stage 1: Build stage
# ==============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# ------------------------------------------------------------------------------
# Build-time environment variables
# ------------------------------------------------------------------------------
ARG VITE_API_BASE_URL
ARG VITE_FIREBASE_API_KEY
ARG VITE_FIREBASE_AUTH_DOMAIN
ARG VITE_FIREBASE_PROJECT_ID
ARG VITE_FIREBASE_STORAGE_BUCKET
ARG VITE_FIREBASE_MESSAGING_SENDER_ID
ARG VITE_FIREBASE_APP_ID
ARG VITE_DEMO_EMAIL
ARG VITE_DEMO_PASSWORD

ENV VITE_API_BASE_URL=${VITE_API_BASE_URL} \
    VITE_FIREBASE_API_KEY=${VITE_FIREBASE_API_KEY} \
    VITE_FIREBASE_AUTH_DOMAIN=${VITE_FIREBASE_AUTH_DOMAIN} \
    VITE_FIREBASE_PROJECT_ID=${VITE_FIREBASE_PROJECT_ID} \
    VITE_FIREBASE_STORAGE_BUCKET=${VITE_FIREBASE_STORAGE_BUCKET} \
    VITE_FIREBASE_MESSAGING_SENDER_ID=${VITE_FIREBASE_MESSAGING_SENDER_ID} \
    VITE_FIREBASE_APP_ID=${VITE_FIREBASE_APP_ID} \
    VITE_DEMO_EMAIL=${VITE_DEMO_EMAIL} \
    VITE_DEMO_PASSWORD=${VITE_DEMO_PASSWORD}

# ------------------------------------------------------------------------------
# Copy dependency manifests first (better Docker layer caching)
# ------------------------------------------------------------------------------
COPY apps/operations-dashboard/package*.json ./

# Install dependencies
RUN npm ci

# ------------------------------------------------------------------------------
# Copy application source
# ------------------------------------------------------------------------------
COPY apps/operations-dashboard/ ./

# Build production bundle
RUN npm run build

# ==============================================================================
# Stage 2: Production Runtime (Nginx)
# ==============================================================================
FROM nginx:1.27-alpine AS runner

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY apps/operations-dashboard/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built frontend
COPY --from=builder /app/dist /usr/share/nginx/html

# Cloud Run listens on 8080
EXPOSE 8080

# Optional health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]