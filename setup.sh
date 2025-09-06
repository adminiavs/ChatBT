#!/bin/bash

# ChatBT Standalone Application Setup Script
# This script sets up the complete ChatBT application environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[SETUP]${NC} $1"
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

echo "🔧 ChatBT Standalone Application Setup"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -d "chatbt-backend" ] || [ ! -d "chatbt-frontend" ]; then
    print_error "Please run this script from the chatbt_standalone_app directory"
    exit 1
fi

# Check system requirements
print_status "Checking system requirements..."

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
print_success "Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed"
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION found"

# Check npm or pnpm
if command -v pnpm &> /dev/null; then
    PACKAGE_MANAGER="pnpm"
    PACKAGE_VERSION=$(pnpm --version)
    print_success "pnpm $PACKAGE_VERSION found (preferred)"
elif command -v npm &> /dev/null; then
    PACKAGE_MANAGER="npm"
    PACKAGE_VERSION=$(npm --version)
    print_success "npm $PACKAGE_VERSION found"
else
    print_error "npm or pnpm is required but not installed"
    exit 1
fi

echo ""

# Setup Backend
print_status "Setting up backend environment..."
cd chatbt-backend

# Check if virtual environment already exists
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, skipping creation"
else
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install backend dependencies
print_status "Installing backend dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install essential dependencies
    pip install flask flask-cors flask-sqlalchemy
fi

# Update requirements.txt
print_status "Updating requirements.txt..."
pip freeze > requirements.txt

print_success "Backend setup completed"

# Setup Frontend
print_status "Setting up frontend environment..."
cd ../chatbt-frontend

# Install frontend dependencies
print_status "Installing frontend dependencies with $PACKAGE_MANAGER..."
if [ "$PACKAGE_MANAGER" = "pnpm" ]; then
    pnpm install
else
    npm install
fi

print_success "Frontend setup completed"

# Return to root directory
cd ..

# Create environment file
print_status "Creating environment configuration..."
if [ ! -f "chatbt-backend/.env" ]; then
    cat > chatbt-backend/.env << EOF
# ChatBT Backend Configuration
FLASK_ENV=development
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=sqlite:///app.db
DEBUG=True

# AI Configuration
EMERGENCE_MONITORING=True
TRAINING_ENABLED=True
MAX_CHAT_HISTORY=100

# API Configuration
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
API_RATE_LIMIT=100
EOF
    print_success "Environment file created"
else
    print_warning "Environment file already exists, skipping"
fi

# Test the setup
print_status "Testing the setup..."

# Test backend
print_status "Testing backend..."
cd chatbt-backend
source venv/bin/activate

# Quick import test
if python3 -c "from src.routes.chatbt import chatbt_bp; print('Backend imports successful')" 2>/dev/null; then
    print_success "Backend test passed"
else
    print_warning "Backend test failed - may need manual configuration"
fi

cd ..

# Test frontend
print_status "Testing frontend..."
cd chatbt-frontend

if [ "$PACKAGE_MANAGER" = "pnpm" ]; then
    if pnpm run build --dry-run &>/dev/null; then
        print_success "Frontend test passed"
    else
        print_warning "Frontend test failed - may need manual configuration"
    fi
else
    print_success "Frontend dependencies installed"
fi

cd ..

# Create quick start guide
print_status "Creating quick start guide..."
cat > QUICK_START.md << 'EOF'
# ChatBT Quick Start Guide

## 🚀 Starting the Application

### Option 1: Use the startup script (Recommended)
```bash
./start.sh
```

### Option 2: Manual startup

1. **Start Backend:**
   ```bash
   cd chatbt-backend
   source venv/bin/activate
   python src/main.py
   ```

2. **Start Frontend (in new terminal):**
   ```bash
   cd chatbt-frontend
   npm run dev  # or pnpm run dev
   ```

## 🌐 Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api

## 🎯 First Steps

1. Open http://localhost:5173 in your browser
2. Start chatting with the AI assistant
3. Ask about Python, Pandas, or programming concepts
4. Watch the emergence monitoring in real-time
5. Try the training features to enhance capabilities

## 🛑 Stopping the Application

- If using `start.sh`: Press Ctrl+C
- If manual: Stop both terminal processes with Ctrl+C

## 🔧 Troubleshooting

- **Port conflicts**: Change ports in configuration files
- **CORS errors**: Check backend CORS configuration
- **Dependencies**: Re-run `./setup.sh`

Enjoy using ChatBT! 🎉
EOF

print_success "Quick start guide created"

# Final summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "✅ Backend environment configured"
echo "✅ Frontend dependencies installed"
echo "✅ Environment variables set"
echo "✅ Quick start guide created"
echo ""
echo "🚀 Next Steps:"
echo "   1. Run: ./start.sh"
echo "   2. Open: http://localhost:5173"
echo "   3. Start chatting with ChatBT!"
echo ""
echo "📚 Documentation:"
echo "   - README.md: Complete documentation"
echo "   - QUICK_START.md: Quick start guide"
echo ""
echo "🆘 Need Help?"
echo "   - Check the troubleshooting section in README.md"
echo "   - Ensure all system requirements are met"
echo "   - Re-run this setup script if needed"
echo ""

print_success "ChatBT is ready to use! 🚀"

