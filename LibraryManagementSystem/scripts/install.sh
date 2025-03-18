#!/bin/bash
# Installation script for the Library Management System

# Exit on error
set -e

# Display help message
display_help() {
    echo "Library Management System - Installation Script"
    echo ""
    echo "Usage: ./install.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help            Display this help message"
    echo "  -d, --dev             Install development dependencies"
    echo "  -c, --client-only     Install client only"
    echo "  -s, --server-only     Install server only"
    echo "  -p, --prefix=DIR      Installation prefix (default: /usr/local)"
    echo ""
    exit 0
}

# Parse command line arguments
INSTALL_DEV=false
INSTALL_CLIENT=true
INSTALL_SERVER=true
INSTALL_PREFIX="/usr/local"

for arg in "$@"; do
    case $arg in
        -h|--help)
            display_help
            ;;
        -d|--dev)
            INSTALL_DEV=true
            ;;
        -c|--client-only)
            INSTALL_CLIENT=true
            INSTALL_SERVER=false
            ;;
        -s|--server-only)
            INSTALL_CLIENT=false
            INSTALL_SERVER=true
            ;;
        -p=*|--prefix=*)
            INSTALL_PREFIX="${arg#*=}"
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

echo "Installing Library Management System..."
echo "Project directory: $PROJECT_DIR"
echo "Installation prefix: $INSTALL_PREFIX"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 8 ]; then
    echo "Error: Python 3.8 or higher is required. Found Python $PYTHON_VERSION."
    exit 1
fi

echo "Python version: $PYTHON_VERSION (OK)"

# Create virtual environment if it doesn't exist
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT_DIR/venv"
fi

# Activate virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install the package
echo "Installing Library Management System..."
if [ "$INSTALL_DEV" = true ]; then
    echo "Installing with development dependencies..."
    pip install -e "$PROJECT_DIR[dev]"
else
    pip install -e "$PROJECT_DIR"
fi

# Create data directories
echo "Creating data directories..."
mkdir -p "$PROJECT_DIR/data/cache"
mkdir -p "$PROJECT_DIR/data/scraped"
mkdir -p "$PROJECT_DIR/logs"

# Create configuration files for different environments
echo "Creating configuration files..."
mkdir -p "$PROJECT_DIR/config"

# Development configuration
if [ ! -f "$PROJECT_DIR/config/development.ini" ]; then
    cat > "$PROJECT_DIR/config/development.ini" << EOF
[database]
path = $PROJECT_DIR/data/library_dev.db
timeout = 30

[server]
host = localhost
port = 9000
max_connections = 10
buffer_size = 4096

[security]
password_salt = library_management_system_dev
token_expiry = 3600

[logging]
level = DEBUG
file = $PROJECT_DIR/logs/library_dev.log
EOF
fi

# Testing configuration
if [ ! -f "$PROJECT_DIR/config/testing.ini" ]; then
    cat > "$PROJECT_DIR/config/testing.ini" << EOF
[database]
path = $PROJECT_DIR/data/library_test.db
timeout = 30

[server]
host = localhost
port = 9001
max_connections = 5
buffer_size = 4096

[security]
password_salt = library_management_system_test
token_expiry = 3600

[logging]
level = INFO
file = $PROJECT_DIR/logs/library_test.log
EOF
fi

# Production configuration
if [ ! -f "$PROJECT_DIR/config/production.ini" ]; then
    cat > "$PROJECT_DIR/config/production.ini" << EOF
[database]
path = $INSTALL_PREFIX/var/lib/library-management-system/library.db
timeout = 30

[server]
host = 0.0.0.0
port = 9000
max_connections = 50
buffer_size = 4096

[security]
password_salt = $(openssl rand -hex 16)
token_expiry = 3600

[logging]
level = WARNING
file = $INSTALL_PREFIX/var/log/library-management-system/library.log
EOF
fi

# Create desktop entries for client and server
if [ "$INSTALL_CLIENT" = true ]; then
    echo "Creating desktop entry for client..."
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/library-management-client.desktop" << EOF
[Desktop Entry]
Name=Library Management System - Client
Comment=Client application for the Library Management System
Exec=$PROJECT_DIR/venv/bin/lms-client
Icon=$PROJECT_DIR/client/resources/icons/app.png
Terminal=false
Type=Application
Categories=Education;Office;
EOF
fi

if [ "$INSTALL_SERVER" = true ]; then
    echo "Creating desktop entry for server..."
    mkdir -p "$HOME/.local/share/applications"
    cat > "$HOME/.local/share/applications/library-management-server.desktop" << EOF
[Desktop Entry]
Name=Library Management System - Server
Comment=Server application for the Library Management System
Exec=$PROJECT_DIR/venv/bin/lms-server
Icon=$PROJECT_DIR/server/resources/icons/app.png
Terminal=true
Type=Application
Categories=Education;Office;
EOF
fi

# Create symbolic links to binaries
if [ "$INSTALL_PREFIX" != "$PROJECT_DIR" ]; then
    echo "Creating symbolic links..."
    mkdir -p "$INSTALL_PREFIX/bin"
    
    if [ "$INSTALL_CLIENT" = true ]; then
        ln -sf "$PROJECT_DIR/venv/bin/lms-client" "$INSTALL_PREFIX/bin/lms-client"
    fi
    
    if [ "$INSTALL_SERVER" = true ]; then
        ln -sf "$PROJECT_DIR/venv/bin/lms-server" "$INSTALL_PREFIX/bin/lms-server"
    fi
fi

# Initialize the database
if [ "$INSTALL_SERVER" = true ]; then
    echo "Initializing the database..."
    python -c "from database.db_manager import initialize_database; initialize_database()"
fi

echo ""
echo "Installation completed successfully!"
echo ""
echo "To run the server:"
echo "  $INSTALL_PREFIX/bin/lms-server"
echo ""
echo "To run the client:"
echo "  $INSTALL_PREFIX/bin/lms-client"
echo ""
echo "For more information, see the documentation in the docs directory."
