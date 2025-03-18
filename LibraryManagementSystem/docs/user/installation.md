# Library Management System - Installation Guide

This guide provides instructions for installing the Library Management System on your computer.

## System Requirements

- Python 3.8 or higher
- SQLite 3
- Network connectivity for client-server communication
- Graphical environment for the client application (PyQt5)

## Installation Methods

There are several ways to install the Library Management System:

### Method 1: Using the Installation Script (Recommended)

1. Download the latest release from the project repository.
2. Extract the archive to a directory of your choice.
3. Open a terminal and navigate to the extracted directory.
4. Run the installation script:

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

This will install the Library Management System in the default location (`/usr/local`). You can customize the installation by using the following options:

- `-h, --help`: Display help message
- `-d, --dev`: Install development dependencies
- `-c, --client-only`: Install client only
- `-s, --server-only`: Install server only
- `-p, --prefix=DIR`: Installation prefix (default: /usr/local)

Example:

```bash
./scripts/install.sh --prefix=$HOME/library-system --dev
```

### Method 2: Using pip

You can also install the Library Management System using pip:

1. Download the latest release from the project repository.
2. Extract the archive to a directory of your choice.
3. Open a terminal and navigate to the extracted directory.
4. Install using pip:

```bash
pip install .
```

For development installation:

```bash
pip install -e ".[dev]"
```

### Method 3: From Source

To install from source:

1. Clone the repository:

```bash
git clone https://github.com/example/library-management-system.git
cd library-management-system
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:

```bash
pip install -e .
```

## Post-Installation

After installation, you need to:

1. Initialize the database (if not done automatically during installation):

```bash
python -c "from database.db_manager import initialize_database; initialize_database()"
```

2. Configure the system by editing the configuration files in the `config` directory.

## Running the Application

### Running the Server

To run the server:

```bash
lms-server
```

Or if you installed using Method 3:

```bash
python -m server.main
```

### Running the Client

To run the client:

```bash
lms-client
```

Or if you installed using Method 3:

```bash
python -m client.main
```

## Troubleshooting

### Common Issues

1. **Connection Error**: If the client cannot connect to the server, check that:
   - The server is running
   - The server address and port in the configuration are correct
   - There are no firewall issues blocking the connection

2. **Database Error**: If there are database errors, check that:
   - The database file exists and is accessible
   - The database schema is correctly initialized
   - The database file is not corrupted

3. **GUI Error**: If the client GUI does not display correctly, check that:
   - PyQt5 is correctly installed
   - Your system supports the required GUI components

### Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the logs in the `logs` directory for error messages
2. Consult the project documentation
3. Contact the project maintainers for support

## Uninstallation

To uninstall the Library Management System:

1. If installed using the installation script:

```bash
./scripts/install.sh --uninstall
```

2. If installed using pip:

```bash
pip uninstall library-management-system
```

3. If installed from source, simply remove the directory and any created symbolic links.
