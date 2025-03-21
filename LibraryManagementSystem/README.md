# Library Management System

## Overview
A comprehensive library management system with user authentication, database, network functionality, data visualization, and analysis capabilities. This system allows libraries to manage their book inventory, track borrowing/returning transactions, and analyze usage patterns.

## Features

### Core Functionality
- **User Interface**: Modern GUI built with PyQt5
- **Database**: SQLite with models for users, books, and transactions
- **Network Module**: Client-server architecture for remote access
- **Authentication**: Secure login/logout with password hashing and JWT tokens
- **Role-Based Access**: Different interfaces for admins and general users

### Admin Features
- **Book Management**: Add, edit, delete, and search books
- **User Management**: Create and manage user accounts with different roles
- **Transaction Tracking**: Monitor all borrowing and returning activities
- **Data Search**: Multi-dimensional search capabilities across all data
- **Reporting**: Generate statistics and reports on library usage
- **Dashboard**: Visual overview of key metrics and trends

### General User Features
- **Book Browsing**: Search and view available books
- **Book Borrowing**: Borrow available books
- **Transaction History**: View personal borrowing history
- **Profile Management**: Update personal information

### Advanced Features
- **Data Visualization**: Charts and graphs using Matplotlib (bar, pie, line, scatter, heatmap)
- **Data Analysis**: Predictive modeling and trend analysis using Pandas and Scikit-learn
- **Web Scraping**: Import book data from online sources using BeautifulSoup4
- **Concurrent Database Control**: Safe multi-user access with transaction management
- **Application Packaging**: Complete with setup scripts and installation guides

## Installation

### Prerequisites
- Python 3.12+
- Git (for version control)

### Dependencies
```
PyQt5>=5.15.0
matplotlib>=3.5.0
numpy>=1.20.0
pandas>=1.3.0
requests>=2.25.0
scikit-learn>=1.0.0
seaborn>=0.11.0
beautifulsoup4>=4.9.0
```

### Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd LibraryManagementSystem
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   # On Linux/Mac:
   python database/db_manager.py
   
   # On Windows:
   # Option 1: Set PYTHONPATH first
   set PYTHONPATH=path\to\LibraryManagementSystem
   python database\db_manager.py
   
   # Option 2: Run as a module
   python -m LibraryManagementSystem.database.db_manager
   ```

4. Run as a package:
   ```
   # Start the server
   python -m LibraryManagementSystem server
   
   # Start the client
   python -m LibraryManagementSystem client
   ```

   Alternatively, you can run the components directly:
   ```
   # On Linux/Mac:
   python server/main.py
   python client/main.py
   
   # On Windows:
   # Option 1: Set PYTHONPATH first
   set PYTHONPATH=path\to\LibraryManagementSystem
   python server\main.py
   python client\main.py
   
   # Option 2: Run as modules
   python -m LibraryManagementSystem.server.main
   python -m LibraryManagementSystem.client.main
   ```

## Usage

### Default Login Credentials
- **Admin User**:
  - Username: admin
  - Password: admin123

- **General User**:
  - Username: user
  - Password: user123

### Basic Workflow
1. **Login**: Start the client application and log in with your credentials
2. **Admin Tasks**:
   - Manage books (add, edit, delete)
   - Manage users (add, edit, delete)
   - View reports and statistics
3. **User Tasks**:
   - Browse available books
   - Borrow books
   - Return books
   - View borrowing history

## Project Structure
```
LibraryManagementSystem/
├── client/                 # Client-side code
│   ├── gui/                # GUI components
│   │   ├── dialogs/        # Dialog windows
│   │   ├── admin_window.py # Admin interface
│   │   ├── login_window.py # Login interface
│   │   └── user_window.py  # User interface
│   ├── network/            # Client network code
│   └── main.py             # Client entry point
├── database/               # Database components
│   ├── models/             # Data models
│   ├── operations/         # Database operations
│   └── db_manager.py       # Database manager
├── server/                 # Server-side code
│   ├── handlers/           # Request handlers
│   ├── network/            # Server network code
│   └── main.py             # Server entry point
├── utils/                  # Utility modules
│   ├── data_analysis.py    # Data analysis tools
│   ├── data_visualization.py # Visualization tools
│   ├── logger.py           # Logging system
│   ├── security.py         # Security utilities
│   └── web_scraping/       # Web scraping tools
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/                   # Documentation
├── scripts/                # Build and installation scripts
├── main.py                 # Main entry point
└── requirements.txt        # Project dependencies
```

## Testing
Run the test suite to verify functionality:
```
python run_tests.py
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure functionality
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
