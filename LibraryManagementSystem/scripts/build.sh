#!/bin/bash
# Build script for the Library Management System

# Exit on error
set -e

# Display help message
display_help() {
    echo "Library Management System - Build Script"
    echo ""
    echo "Usage: ./build.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help            Display this help message"
    echo "  -c, --clean           Clean build artifacts before building"
    echo "  -d, --dist            Create distribution packages"
    echo "  -t, --test            Run tests before building"
    echo "  -o, --output=DIR      Output directory (default: ./dist)"
    echo ""
    exit 0
}

# Parse command line arguments
CLEAN_BUILD=false
CREATE_DIST=false
RUN_TESTS=false
OUTPUT_DIR="./dist"

for arg in "$@"; do
    case $arg in
        -h|--help)
            display_help
            ;;
        -c|--clean)
            CLEAN_BUILD=true
            ;;
        -d|--dist)
            CREATE_DIST=true
            ;;
        -t|--test)
            RUN_TESTS=true
            ;;
        -o=*|--output=*)
            OUTPUT_DIR="${arg#*=}"
            ;;
        *)
            echo "Unknown option: $arg"
            display_help
            ;;
    esac
done

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Building Library Management System..."
echo "Project directory: $PROJECT_DIR"
echo "Output directory: $OUTPUT_DIR"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Clean build artifacts if requested
if [ "$CLEAN_BUILD" = true ]; then
    echo "Cleaning build artifacts..."
    rm -rf "$PROJECT_DIR/build"
    rm -rf "$PROJECT_DIR/dist"
    rm -rf "$PROJECT_DIR/*.egg-info"
    find "$PROJECT_DIR" -name "__pycache__" -type d -exec rm -rf {} +
    find "$PROJECT_DIR" -name "*.pyc" -delete
    find "$PROJECT_DIR" -name "*.pyo" -delete
    find "$PROJECT_DIR" -name "*.pyd" -delete
    find "$PROJECT_DIR" -name ".pytest_cache" -type d -exec rm -rf {} +
    find "$PROJECT_DIR" -name ".coverage" -delete
    find "$PROJECT_DIR" -name "htmlcov" -type d -exec rm -rf {} +
fi

# Run tests if requested
if [ "$RUN_TESTS" = true ]; then
    echo "Running tests..."
    cd "$PROJECT_DIR"
    python -m pytest
fi

# Create client resources directory if it doesn't exist
mkdir -p "$PROJECT_DIR/client/resources/icons"

# Create server resources directory if it doesn't exist
mkdir -p "$PROJECT_DIR/server/resources/icons"

# Create application icon if it doesn't exist
if [ ! -f "$PROJECT_DIR/client/resources/icons/app.png" ]; then
    echo "Creating application icon..."
    # Use a placeholder icon (a colored square)
    convert -size 128x128 xc:blue "$PROJECT_DIR/client/resources/icons/app.png"
fi

if [ ! -f "$PROJECT_DIR/server/resources/icons/app.png" ]; then
    echo "Creating server icon..."
    # Use a placeholder icon (a colored square)
    convert -size 128x128 xc:green "$PROJECT_DIR/server/resources/icons/app.png"
fi

# Create README.md if it doesn't exist
if [ ! -f "$PROJECT_DIR/README.md" ]; then
    echo "Creating README.md..."
    cat > "$PROJECT_DIR/README.md" << EOF
# Library Management System

A comprehensive library management system with client-server architecture.

## Features

- User authentication and role-based access control
- Book management (add, edit, delete, search)
- User management (add, edit, delete, search)
- Transaction management (borrow, return, track)
- Data visualization and analysis
- Web scraping for book information

## Installation

See the [installation guide](docs/user/installation.md) for detailed instructions.

## Usage

See the [usage guide](docs/user/usage.md) for detailed instructions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
EOF
fi

# Create LICENSE file if it doesn't exist
if [ ! -f "$PROJECT_DIR/LICENSE" ]; then
    echo "Creating LICENSE file..."
    cat > "$PROJECT_DIR/LICENSE" << EOF
MIT License

Copyright (c) $(date +%Y) Library Management Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
fi

# Create MANIFEST.in if it doesn't exist
if [ ! -f "$PROJECT_DIR/MANIFEST.in" ]; then
    echo "Creating MANIFEST.in..."
    cat > "$PROJECT_DIR/MANIFEST.in" << EOF
include LICENSE
include README.md
include MANIFEST.in
recursive-include config *.ini
recursive-include client/resources *
recursive-include server/resources *
recursive-include docs *
EOF
fi

# Create distribution packages if requested
if [ "$CREATE_DIST" = true ]; then
    echo "Creating distribution packages..."
    cd "$PROJECT_DIR"
    python setup.py sdist bdist_wheel
    
    # Copy distribution packages to output directory
    cp "$PROJECT_DIR/dist"/* "$OUTPUT_DIR/"
    
    echo "Distribution packages created in $OUTPUT_DIR"
else
    # Create a simple executable package
    echo "Creating executable package..."
    
    # Create package directory
    PACKAGE_DIR="$OUTPUT_DIR/library-management-system"
    mkdir -p "$PACKAGE_DIR"
    
    # Copy project files
    cp -r "$PROJECT_DIR"/* "$PACKAGE_DIR/"
    
    # Remove unnecessary files
    rm -rf "$PACKAGE_DIR/build"
    rm -rf "$PACKAGE_DIR/dist"
    rm -rf "$PACKAGE_DIR/*.egg-info"
    find "$PACKAGE_DIR" -name "__pycache__" -type d -exec rm -rf {} +
    find "$PACKAGE_DIR" -name "*.pyc" -delete
    find "$PACKAGE_DIR" -name "*.pyo" -delete
    find "$PACKAGE_DIR" -name "*.pyd" -delete
    find "$PACKAGE_DIR" -name ".pytest_cache" -type d -exec rm -rf {} +
    find "$PACKAGE_DIR" -name ".coverage" -delete
    find "$PACKAGE_DIR" -name "htmlcov" -type d -exec rm -rf {} +
    
    # Create launcher scripts
    echo "Creating launcher scripts..."
    
    # Client launcher
    cat > "$PACKAGE_DIR/lms-client.sh" << EOF
#!/bin/bash
# Library Management System - Client Launcher

# Get the script directory
SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"

# Create virtual environment if it doesn't exist
if [ ! -d "\$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "\$SCRIPT_DIR/venv"
    
    # Activate virtual environment
    source "\$SCRIPT_DIR/venv/bin/activate"
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -e "\$SCRIPT_DIR"
else
    # Activate virtual environment
    source "\$SCRIPT_DIR/venv/bin/activate"
fi

# Run client
python -m client.main

# Deactivate virtual environment
deactivate
EOF
    
    # Server launcher
    cat > "$PACKAGE_DIR/lms-server.sh" << EOF
#!/bin/bash
# Library Management System - Server Launcher

# Get the script directory
SCRIPT_DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"

# Create virtual environment if it doesn't exist
if [ ! -d "\$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "\$SCRIPT_DIR/venv"
    
    # Activate virtual environment
    source "\$SCRIPT_DIR/venv/bin/activate"
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -e "\$SCRIPT_DIR"
else
    # Activate virtual environment
    source "\$SCRIPT_DIR/venv/bin/activate"
fi

# Initialize database if it doesn't exist
if [ ! -f "\$SCRIPT_DIR/data/library.db" ]; then
    echo "Initializing database..."
    python -c "from database.db_manager import initialize_database; initialize_database()"
fi

# Run server
python -m server.main

# Deactivate virtual environment
deactivate
EOF
    
    # Make launcher scripts executable
    chmod +x "$PACKAGE_DIR/lms-client.sh"
    chmod +x "$PACKAGE_DIR/lms-server.sh"
    
    echo "Executable package created in $PACKAGE_DIR"
fi

echo ""
echo "Build completed successfully!"
