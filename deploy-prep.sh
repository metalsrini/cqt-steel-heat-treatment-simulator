#!/bin/bash

# C-Q-T Steel Heat Treatment Simulator - Deployment Preparation Script
# This script prepares your application for deployment to Render.com

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Main deployment preparation function
main() {
    print_header "C-Q-T Steel Heat Treatment Simulator - Deployment Prep"
    
    # Check if we're in the right directory
    if [ ! -d "web_application" ] || [ ! -f "README.md" ]; then
        print_error "Please run this script from the project root directory (zed AI/)"
        exit 1
    fi
    
    print_status "Starting deployment preparation..."
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Step 2: Test backend locally
    test_backend
    
    # Step 3: Test frontend locally
    test_frontend
    
    # Step 4: Create production environment files
    create_production_configs
    
    # Step 5: Validate deployment files
    validate_deployment_files
    
    # Step 6: Git preparation
    prepare_git_repository
    
    # Step 7: Display deployment instructions
    show_deployment_instructions
    
    print_success "Deployment preparation completed successfully!"
}

# Check if all required tools are installed
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js found: $NODE_VERSION"
    else
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        print_success "npm found: $NPM_VERSION"
    else
        print_error "npm is required but not installed"
        exit 1
    fi
    
    # Check git
    if command -v git &> /dev/null; then
        print_success "Git found"
    else
        print_error "Git is required but not installed"
        exit 1
    fi
}

# Test backend functionality
test_backend() {
    print_header "Testing Backend"
    
    cd web_application/backend
    
    # Install backend dependencies if needed
    if [ ! -d "../../__pycache__" ]; then
        print_status "Installing backend dependencies..."
        pip3 install -r requirements.txt > /dev/null 2>&1 || {
            print_warning "Some dependencies might not be installed. Continuing..."
        }
    fi
    
    # Test backend imports
    print_status "Testing backend imports..."
    python3 -c "
import sys
sys.path.insert(0, '../..')
try:
    from core.mathematical_models.phase_transformation import PhaseTransformationModels
    from core.mathematical_models.carbon_diffusion import CarbonDiffusionModels
    from case_depth_integration import IntegratedCaseDepthModel
    import main
    print('✓ All imports successful')
except Exception as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
" || {
        print_error "Backend import test failed"
        exit 1
    }
    
    print_success "Backend tests passed"
    cd ../..
}

# Test frontend functionality
test_frontend() {
    print_header "Testing Frontend"
    
    cd web_application/frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install > /dev/null 2>&1
    fi
    
    # Test frontend build
    print_status "Testing frontend build..."
    npm run build > /dev/null 2>&1 || {
        print_error "Frontend build failed"
        exit 1
    }
    
    # Clean build directory for deployment
    rm -rf build/
    
    print_success "Frontend tests passed"
    cd ../..
}

# Create production configuration files
create_production_configs() {
    print_header "Creating Production Configurations"
    
    # Create backend .env file if it doesn't exist
    if [ ! -f "web_application/backend/.env" ]; then
        print_status "Creating backend .env file..."
        cat > web_application/backend/.env << EOF
# Production Environment Configuration
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info
ALLOWED_ORIGINS=https://your-frontend-app.onrender.com
RELOAD=false
MAX_REQUESTS_PER_MINUTE=100
MAX_SIMULATION_TIME_SECONDS=300
MAX_SPATIAL_POINTS=201
EOF
        print_success "Backend .env created"
    else
        print_success "Backend .env already exists"
    fi
    
    # Update frontend production environment
    print_status "Updating frontend production environment..."
    cat > web_application/frontend/.env.production << EOF
REACT_APP_API_URL=https://your-backend-app.onrender.com
DISABLE_ESLINT_PLUGIN=true
REACT_APP_APP_NAME=C-Q-T Steel Heat Treatment Simulator
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=production
REACT_APP_TIMEOUT=300000
REACT_APP_DEBUG=false
REACT_APP_LOG_LEVEL=warn
GENERATE_SOURCEMAP=false
PUBLIC_URL=.
EOF
    print_success "Frontend production environment updated"
}

# Validate all deployment files exist
validate_deployment_files() {
    print_header "Validating Deployment Files"
    
    REQUIRED_FILES=(
        "web_application/backend/main.py"
        "web_application/backend/requirements.txt"
        "web_application/frontend/package.json"
        "web_application/frontend/.env.production"
        "render.yaml"
        "DEPLOYMENT.md"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            print_success "✓ $file"
        else
            print_error "✗ Missing: $file"
            exit 1
        fi
    done
    
    print_success "All deployment files validated"
}

# Prepare git repository
prepare_git_repository() {
    print_header "Preparing Git Repository"
    
    # Check if we're in a git repository
    if [ ! -d ".git" ]; then
        print_status "Initializing git repository..."
        git init
        git add .
        git commit -m "Initial commit - C-Q-T Steel Heat Treatment Simulator"
    fi
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        print_status "Found uncommitted changes. Adding and committing..."
        git add .
        git commit -m "Prepare for Render deployment - $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    print_success "Git repository is ready"
    
    # Check if remote origin exists
    if ! git remote get-url origin &> /dev/null; then
        print_warning "No remote origin set. You'll need to push to GitHub before deploying to Render."
        print_status "To add a remote origin:"
        echo "  git remote add origin https://github.com/yourusername/your-repo.git"
        echo "  git branch -M main"
        echo "  git push -u origin main"
    else
        print_status "Pushing to remote repository..."
        git push origin main || {
            print_warning "Push failed. You may need to resolve conflicts or set up authentication."
        }
    fi
}

# Show deployment instructions
show_deployment_instructions() {
    print_header "Deployment Instructions"
    
    echo -e "${GREEN}🎉 Your application is ready for deployment!${NC}\n"
    
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. 📋 Make sure your code is pushed to GitHub"
    echo "2. 🌐 Go to https://render.com and sign up/log in"
    echo "3. 🔧 Create Backend Service:"
    echo "   - Click 'New +' → 'Web Service'"
    echo "   - Connect your GitHub repository"
    echo "   - Name: cqt-steel-simulator-backend"
    echo "   - Environment: Python 3"
    echo "   - Build Command: cd web_application/backend && pip install -r requirements.txt"
    echo "   - Start Command: cd web_application/backend && python main.py"
    echo "   - Add environment variables from web_application/backend/.env"
    echo ""
    echo "4. 🎨 Create Frontend Service:"
    echo "   - Click 'New +' → 'Static Site'"
    echo "   - Connect the same GitHub repository"
    echo "   - Name: cqt-steel-simulator-frontend"
    echo "   - Build Command: cd web_application/frontend && npm ci && npm run build"
    echo "   - Publish Directory: web_application/frontend/build"
    echo "   - Add environment variables from web_application/frontend/.env.production"
    echo ""
    echo "5. 🔗 Update URLs:"
    echo "   - Update backend ALLOWED_ORIGINS with your frontend URL"
    echo "   - Update frontend REACT_APP_API_URL with your backend URL"
    echo ""
    echo "6. ✅ Test your deployed application!"
    echo ""
    
    echo -e "${YELLOW}Important URLs to note:${NC}"
    echo "- Backend will be: https://cqt-steel-simulator-backend.onrender.com"
    echo "- Frontend will be: https://cqt-steel-simulator-frontend.onrender.com"
    echo "- API Health Check: https://your-backend-url.onrender.com/api/health"
    echo "- API Documentation: https://your-backend-url.onrender.com/api/docs"
    echo ""
    
    echo -e "${GREEN}📖 For detailed instructions, see DEPLOYMENT.md${NC}"
    echo ""
    
    print_success "Ready to deploy to Render! 🚀"
}

# Run the main function
main "$@"