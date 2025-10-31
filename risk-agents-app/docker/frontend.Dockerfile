# Frontend Dockerfile - Node 20 for Next.js 15
# This creates a container for the Next.js frontend

FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first (for Docker layer caching)
# If dependencies don't change, this layer is reused
COPY frontend/package*.json ./

# Install dependencies
# Using npm install (will create package-lock.json if it doesn't exist)
RUN npm install

# Copy application code
# This is done after dependencies so code changes don't invalidate dependency cache
COPY frontend/ .

# Expose port 3050 (our frontend port)
EXPOSE 3050

# Run Next.js in development mode
# This enables hot-reloading and better error messages
CMD ["npm", "run", "dev"]
