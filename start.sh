#!/bin/bash

# ChatBT Standalone Application Startup Script
# This script starts both the backend and frontend servers

set -e

echo "🚀 Starting ChatBT Standalone Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[ChatBT]${NC} $1"
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

# Check if we're in the right directory
if [ ! -d "chatbt-backend" ] || [ ! -d "chatbt-frontend" ]; then
    print_error "Please run this script from the chatbt_standalone_app directory"
    exit 1
fi

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

# Check required ports
print_status "Checking required ports..."
if ! check_port 5000; then
    print_warning "Port 5000 is already in use. Backend may conflict."
fi

if ! check_port 5173; then
    print_warning "Port 5173 is already in use. Frontend may conflict."
fi

# Start backend server
print_status "Starting backend server..."
cd chatbt-backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment and start backend
source venv/bin/activate

# Check if Flask-CORS is installed
if ! python -c "import flask_cors" 2>/dev/null; then
    print_status "Installing Flask-CORS..."
    pip install flask-cors
fi

# Start backend in background
print_status "Launching Flask backend on port 5000..."
python src/main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    print_error "Backend failed to start"
    exit 1
fi

print_success "Backend started successfully (PID: $BACKEND_PID)"

# Start frontend server
print_status "Starting frontend server..."
cd ../chatbt-frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    if command -v pnpm &> /dev/null; then
        pnpm install
    else
        npm install
    fi
fi

# Start frontend in background
print_status "Launching React frontend on port 5173..."
if command -v pnpm &> /dev/null; then
    pnpm run dev --host &
else
    npm run dev -- --host &
fi
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    print_error "Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

print_success "Frontend started successfully (PID: $FRONTEND_PID)"

# Display startup information
echo ""
echo "🎉 ChatBT Application Started Successfully!"
echo ""
echo "📊 Application URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:5000"
echo "   API Docs: http://localhost:5000/api"
echo ""
echo "🔧 Process Information:"
echo "   Backend PID:  $BACKEND_PID"
echo "   Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 Usage:"
echo "   - Open http://localhost:5173 in your browser"
echo "   - Start chatting with the AI assistant"
echo "   - Monitor emergence scores in real-time"
echo "   - Use training features to enhance capabilities"
echo ""
echo "🛑 To stop the application:"
echo "   - Press Ctrl+C to stop this script"
echo "   - Or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Create PID file for easy cleanup
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

print_status "Application is ready! Press Ctrl+C to stop..."

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down ChatBT application..."
    
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            print_status "Stopping backend server (PID: $BACKEND_PID)..."
            kill $BACKEND_PID
        fi
        rm -f .backend.pid
    fi
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_status "Stopping frontend server (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
        fi
        rm -f .frontend.pid
    fi
    
    print_success "ChatBT application stopped successfully"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop the application
while true; do
    sleep 1
    
    # Check if processes are still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        print_error "Backend process died unexpectedly"
        cleanup
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        print_error "Frontend process died unexpectedly"
        cleanup
    fi
done

