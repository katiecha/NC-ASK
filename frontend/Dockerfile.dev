# Frontend Dockerfile for NC-ASK
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies (use npm install since we don't have package-lock.json)
RUN npm install

# Copy frontend source code
COPY frontend/ .

# Expose port
EXPOSE 5173

# Start the development server
CMD ["npm", "run", "dev"]
