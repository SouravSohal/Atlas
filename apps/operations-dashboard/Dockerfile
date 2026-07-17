# ==============================================================================
# Stage 1: Build stage
# ==============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package management files to optimize Docker layer caching
COPY apps/operations-dashboard/package*.json ./

# Install dependencies
RUN npm ci

# Copy application files
COPY apps/operations-dashboard/ ./

# Build the Vite application for production
RUN npm run build

# ==============================================================================
# Stage 2: Production Nginx Runtime stage
# ==============================================================================
FROM nginx:alpine AS runner

# Copy custom Nginx configuration
COPY apps/operations-dashboard/nginx.conf /etc/nginx/conf.d/default.conf

# Copy static built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose Nginx listener port
EXPOSE 8080

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
