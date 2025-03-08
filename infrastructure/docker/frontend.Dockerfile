# ========================================
# Stage 1: Builder stage
# Build the React application
# ========================================
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Add build dependencies and clean cache in same layer
RUN apk add --no-cache git python3 make g++ && \
    rm -rf /var/cache/apk/*

# Copy package.json and yarn.lock for better layer caching
# This allows Docker to cache the dependency installation step
COPY ./src/web/package.json ./src/web/yarn.lock ./

# Install dependencies with frozen lockfile for reproducibility
# Set network timeout to handle potential network issues
RUN yarn install --frozen-lockfile --network-timeout 600000 && \
    yarn cache clean

# Copy the rest of the application code
COPY ./src/web/ ./

# Set build arguments for environment configuration
ARG REACT_APP_API_URL
ARG REACT_APP_AUTH0_DOMAIN
ARG REACT_APP_AUTH0_CLIENT_ID
ARG REACT_APP_AUTH0_AUDIENCE

# Set environment variables for the build process
ENV NODE_ENV=production
ENV REACT_APP_API_URL=${REACT_APP_API_URL}
ENV REACT_APP_AUTH0_DOMAIN=${REACT_APP_AUTH0_DOMAIN}
ENV REACT_APP_AUTH0_CLIENT_ID=${REACT_APP_AUTH0_CLIENT_ID}
ENV REACT_APP_AUTH0_AUDIENCE=${REACT_APP_AUTH0_AUDIENCE}

# Build the application for production
RUN yarn build

# Generate source maps for production monitoring
RUN yarn analyze

# ========================================
# Stage 2: Security scanning stage
# Scan the built application for vulnerabilities
# ========================================
FROM aquasec/trivy:latest AS security-scan

# Copy the built application from the builder stage
COPY --from=builder /app/build /app/build

# Run Trivy to scan for vulnerabilities
# Exit with error if critical vulnerabilities are found
RUN trivy filesystem --exit-code 1 --severity CRITICAL /app/build

# ========================================
# Stage 3: Production stage
# Serve the React application using Nginx
# ========================================
FROM nginx:1.23-alpine AS production

# Copy the built application from the builder stage to the Nginx html directory
COPY --from=builder /app/build /usr/share/nginx/html

# Copy our custom Nginx configuration
COPY ./src/web/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for HTTP traffic
EXPOSE 80

# Start Nginx server in foreground mode to keep container running
CMD ["nginx", "-g", "daemon off;"]