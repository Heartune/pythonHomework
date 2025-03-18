# Library Management System - Usage Guide

This guide provides instructions for using the Library Management System.

## Getting Started

### Starting the Server

Before using the client application, you need to start the server:

1. Open a terminal and run:

```bash
lms-server
```

2. The server will start and display a message indicating it's running.
3. Keep the server terminal open while using the client application.

### Starting the Client

To start the client application:

1. Open a terminal and run:

```bash
lms-client
```

2. The login window will appear.

## User Authentication

### Logging In

1. Enter your username and password in the login window.
2. Select your role (User or Admin).
3. Click the "Login" button.

If your credentials are valid and you have the selected role, you will be logged in and the appropriate window (user or admin) will be displayed.

### Logging Out

To log out:

1. Click the "Logout" button in the top-right corner of the window.
2. You will be returned to the login window.

## User Interface

### Admin Interface

The admin interface consists of several tabs:

#### Dashboard

The dashboard provides an overview of the library system:

- Total number of books
- Total number of users
- Recent transactions
- Statistical charts

#### Books

The Books tab allows you to manage the library's book collection:

- View all books in a table
- Search for books by title, author, ISBN, etc.
- Add new books
- Edit existing books
- Delete books
- Import books from external sources

##### Adding a Book

1. Click the "Add Book" button.
2. Fill in the book details in the dialog:
   - Title
   - Author
   - ISBN
   - Publisher
   - Publication Year
   - Category
   - Quantity
   - Description
3. Click "OK" to add the book.

##### Editing a Book

1. Select a book in the table.
2. Click the "Edit" button.
3. Modify the book details in the dialog.
4. Click "OK" to save the changes.

##### Deleting a Book

1. Select a book in the table.
2. Click the "Delete" button.
3. Confirm the deletion in the dialog.

##### Importing Books

1. Click the "Import Books" button.
2. In the dialog, you can:
   - Search for books online by entering a query
   - Import books from a file (JSON or CSV)
3. Select the books you want to import.
4. Click "OK" to import the selected books.

#### Users

The Users tab allows you to manage the system's users:

- View all users in a table
- Search for users by username, name, etc.
- Add new users
- Edit existing users
- Delete users

##### Adding a User

1. Click the "Add User" button.
2. Fill in the user details in the dialog:
   - Username
   - Password
   - Full Name
   - Email
   - Phone
   - Address
   - Role (User or Admin)
3. Click "OK" to add the user.

##### Editing a User

1. Select a user in the table.
2. Click the "Edit" button.
3. Modify the user details in the dialog.
4. Click "OK" to save the changes.

##### Deleting a User

1. Select a user in the table.
2. Click the "Delete" button.
3. Confirm the deletion in the dialog.

#### Reports

The Reports tab allows you to generate and view various reports:

- Books by category
- Books by popularity
- User activity
- Overdue books

To generate a report:

1. Select the report type from the dropdown menu.
2. Set any filters or parameters.
3. Click the "Generate" button.
4. The report will be displayed in the report area.

You can export reports to CSV or PDF by clicking the "Export" button.

### User Interface

The user interface consists of several tabs:

#### Browse Books

The Browse Books tab allows you to browse and search for books:

- View available books in a table
- Search for books by title, author, ISBN, etc.
- View book details

##### Searching for Books

1. Enter your search query in the search box.
2. Select the search criteria (Title, Author, ISBN, etc.).
3. Click the "Search" button.
4. The results will be displayed in the table.

##### Viewing Book Details

1. Select a book in the table.
2. Click the "View Details" button.
3. The book details will be displayed in a dialog.

#### My Books

The My Books tab shows the books you have borrowed:

- Currently borrowed books
- Borrowing history
- Overdue books

##### Borrowing a Book

1. Find the book you want to borrow in the Browse Books tab.
2. Select the book in the table.
3. Click the "Borrow" button.
4. Confirm the borrowing in the dialog.

##### Returning a Book

1. Go to the My Books tab.
2. Select the book you want to return in the table.
3. Click the "Return" button.
4. Confirm the return in the dialog.

#### Profile

The Profile tab allows you to view and edit your profile:

- View your account details
- Edit your personal information
- Change your password

##### Editing Your Profile

1. Modify your personal information in the form.
2. Click the "Save" button to save the changes.

##### Changing Your Password

1. Click the "Change Password" button.
2. Enter your current password and new password in the dialog.
3. Click "OK" to change your password.

## Advanced Features

### Data Visualization

The system includes various data visualization features:

- Bar charts for book categories
- Pie charts for book popularity
- Line charts for user activity
- Heatmaps for borrowing patterns

To access these visualizations:

1. Go to the Reports tab (Admin interface) or the Statistics tab (User interface).
2. Select the visualization type from the dropdown menu.
3. Set any filters or parameters.
4. Click the "Generate" button.

### Data Analysis

The system includes data analysis features:

- Trend analysis for book popularity
- User activity analysis
- Predictive modeling for book demand

To access these analyses:

1. Go to the Reports tab (Admin interface).
2. Select the analysis type from the dropdown menu.
3. Set any filters or parameters.
4. Click the "Generate" button.

### Web Scraping

The system can scrape book information from external sources:

- Search for books online
- Import book details by ISBN
- Schedule regular data collection

To use the web scraping features:

1. Go to the Books tab (Admin interface).
2. Click the "Import Books" button.
3. In the dialog, enter a search query or ISBN.
4. Click the "Search" button.
5. Select the books you want to import.
6. Click "OK" to import the selected books.

## Troubleshooting

### Common Issues

1. **Connection Error**: If you see a "Connection Error" message when starting the client, check that:
   - The server is running
   - The server address and port in the configuration are correct
   - There are no firewall issues blocking the connection

2. **Login Error**: If you cannot log in, check that:
   - Your username and password are correct
   - You have selected the correct role
   - The server is running

3. **Book Not Available**: If a book is not available for borrowing, it may be:
   - Already borrowed by another user
   - Out of stock
   - Reserved for reference only

### Getting Help

If you encounter any issues not covered in this guide, please:

1. Check the logs in the `logs` directory for error messages
2. Consult the project documentation
3. Contact the system administrator for support

## Keyboard Shortcuts

The application supports the following keyboard shortcuts:

- **Ctrl+F**: Open search dialog
- **Ctrl+N**: Add new item (book or user, depending on the current tab)
- **Ctrl+E**: Edit selected item
- **Delete**: Delete selected item
- **F5**: Refresh current view
- **Ctrl+P**: Print current view
- **Ctrl+S**: Save changes
- **Ctrl+Q**: Quit application
