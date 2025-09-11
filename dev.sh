#!/bin/bash

# Development Docker Compose Script for The Globe Blog
# This script provides live reloading for both frontend and backend

set -e

echo "🚀 Starting The Globe Blog in Development Mode with Live Reloading"
echo "============================================================"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping development environment..."
    docker-compose -f docker-compose.dev.yml down
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Stop any existing containers
echo "🧹 Cleaning up existing containers..."
docker-compose -f docker-compose.dev.yml down || true

# Start the development environment
echo "🏗️  Building and starting development containers..."
docker-compose -f docker-compose.dev.yml up --build

# This point will only be reached if docker-compose is interrupted
cleanup
