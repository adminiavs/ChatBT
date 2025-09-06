#!/bin/bash

echo "Installing improved ChatBT backend dependencies..."

# Activate virtual environment
source venv/bin/activate

# Install improved requirements
pip install -r requirements_improved.txt

# Install additional dependencies for production
pip install python-dotenv gunicorn eventlet

echo "Backend dependencies installed successfully!"

# Replace main.py with improved version
if [ -f "src/main_improved.py" ]; then
    echo "Backing up original main.py..."
    cp src/main.py src/main_original.py
    
    echo "Installing improved main.py..."
    cp src/main_improved.py src/main.py
    echo "Main application updated!"
fi

# Replace routes with improved version
if [ -f "src/routes/chatbt_improved.py" ]; then
    echo "Backing up original chatbt.py routes..."
    cp src/routes/chatbt.py src/routes/chatbt_original.py
    
    echo "Installing improved chatbt routes..."
    cp src/routes/chatbt_improved.py src/routes/chatbt.py
    echo "Routes updated!"
fi

echo "All improvements installed successfully!"
echo "You can now start the server with: python src/main.py"

