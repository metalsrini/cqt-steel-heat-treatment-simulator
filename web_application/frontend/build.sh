#!/bin/bash

# Build script for C-Q-T Steel Heat Treatment Simulator Frontend
# This script prepares the React application for production deployment

set -e  # Exit on any error

echo "🚀 Starting frontend build process..."

# Ensure we're in the frontend directory
cd "$(dirname "$0")"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Make sure you're in the frontend directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --production=false

# Clear any previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/

# Set production environment variables
export NODE_ENV=production
export GENERATE_SOURCEMAP=false
export REACT_APP_ENVIRONMENT=production

# Build the application
echo "🔨 Building React application for production..."
npm run build

# Verify build was successful
if [ -d "build" ] && [ -f "build/index.html" ]; then
    echo "✅ Build completed successfully!"
    echo "📁 Build output available in: $(pwd)/build"
    
    # Show build size
    echo "📊 Build size:"
    du -sh build/
    
    # List main build files
    echo "📋 Main build files:"
    ls -la build/
    
else
    echo "❌ Build failed - build directory or index.html not found"
    exit 1
fi

echo "🎉 Frontend build process completed!"