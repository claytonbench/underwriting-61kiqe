# Base image for all stages
FROM node:18-alpine AS base
WORKDIR /app

# Development stage for hot-reloading during development
FROM base AS development
ENV NODE_ENV=development

# Copy package files for dependency installation
COPY package.json yarn.lock ./
RUN yarn install

# Copy all source files
COPY . .

# Expose port 3000 for development server
EXPOSE 3000

# Start development server with hot reloading
CMD ["yarn", "start"]

# Builder stage for creating optimized production build
FROM base AS builder
ENV NODE_ENV=production

# Build arguments for environment configuration
ARG REACT_APP_API_URL
ARG REACT_APP_AUTH0_DOMAIN
ARG REACT_APP_AUTH0_CLIENT_ID
ARG REACT_APP_AUTH0_AUDIENCE

# Set environment variables from build args
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
ENV REACT_APP_AUTH0_DOMAIN=${REACT_APP_AUTH0_DOMAIN}
ENV REACT_APP_AUTH0_CLIENT_ID=${REACT_APP_AUTH0_CLIENT_ID}
ENV REACT_APP_AUTH0_AUDIENCE=${REACT_APP_AUTH0_AUDIENCE}

# Copy package files first for better layer caching
COPY package.json yarn.lock ./
RUN yarn install --frozen-lockfile --production=false

# Copy application source
COPY . .

# Build the production-ready frontend application
RUN yarn build

# Production stage using Nginx to serve static files
FROM nginx:1.23-alpine AS production

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Install curl for health checks
RUN apk add --no-cache curl

# Add container health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost/health || exit 1

# Expose port 80 for web server
EXPOSE 80

# Start Nginx in foreground mode
CMD ["nginx", "-g", "daemon off;"]