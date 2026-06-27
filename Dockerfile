# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Build the FastAPI backend and serve
FROM python:3.11-slim AS backend-runner

# Install system dependencies for OCR and PDF processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    poppler-utils \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code and other directories
COPY backend/ ./backend/
COPY data/ ./data/

# Ensure uploads and chroma_db directories exist with correct permissions
RUN mkdir -p uploads chroma_db && chmod 777 uploads chroma_db

# Copy built static frontend files from Stage 1
COPY --from=frontend-builder /app/dist ./dist

# Set environment variables
ENV PORT=8080
ENV UPLOAD_DIR=/app/uploads

# Expose port and run the FastAPI application
EXPOSE 8080
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
