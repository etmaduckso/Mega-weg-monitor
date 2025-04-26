FROM node:20-slim

WORKDIR /app

# Install wget for healthcheck
RUN apt-get update && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy package files first for better caching
COPY package*.json ./

# Clean install dependencies with legacy peer deps to handle MUI version requirements
RUN npm install -g npm@latest && \
    npm ci --legacy-peer-deps

# Copy rest of the application
COPY . .

# Build the application
ENV NODE_ENV=production
ENV VITE_API_URL=http://localhost:5000

EXPOSE 5173

# Use --host to allow external connections
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]