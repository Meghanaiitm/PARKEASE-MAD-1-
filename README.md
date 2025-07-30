# ParkEase - Parking Management System

A comprehensive web-based parking management solution built with Flask and SQLite. The system provides separate interfaces for users and administrators, supporting multiple vehicles per user and complete parking lot management.

## System Overview

ParkEase enables users to register multiple vehicles, book parking spots, and manage their bookings. Administrators can oversee all users, manage parking lots, and monitor system statistics.

## Core Features

### User Interface
- Vehicle registration and management
- Parking spot booking for specific vehicles
- Booking history and status tracking
- Profile and vehicle information updates
- Booking statistics by date and vehicle

### Administrator Interface
- User and vehicle management
- Parking lot administration
- Booking oversight and management
- System statistics and analytics
- Revenue tracking and reporting

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with Quicksand font and responsive design
- **Authentication**: Session-based login system

## Design System

The application features a modern, professional design with:
- **Typography**: Quicksand font family for clean, readable text
- **Color Scheme**: Deep blue (#1E3A8A) primary color with white text
- **Layout**: Clean, minimalist design without gradients
- **Responsive**: Mobile-friendly interface with adaptive layouts
- **Consistency**: Unified styling across all pages and components

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation Steps

1. Clone or download the project files
2. Navigate to the project directory
3. Install required dependencies:
   ```bash
   pip install flask
   ```
4. Initialize the database:
   ```bash
   python database.py
   ```
5. Run the application:
   ```bash
   python app.py
   ```
6. Access the system at `http://localhost:5000`

## Database Structure

The system uses SQLite with the following main tables:
- **users**: User account information
- **vehicles**: Vehicle details linked to users
- **parking_lot**: Parking lot information
- **parking_spot**: Individual parking spots
- **booking**: Booking records with vehicle associations

## User Workflow

1. **Registration**: Create account with personal details
2. **Vehicle Management**: Add multiple vehicles to account
3. **Booking**: Select parking lot and spot for specific vehicle
4. **Management**: View and manage current bookings
5. **History**: Access booking history and statistics

## Administrator Workflow

1. **Login**: Access admin interface with credentials
2. **User Management**: View and manage user accounts
3. **Parking Management**: Add, edit, and monitor parking lots
4. **Booking Oversight**: Review and manage all bookings
5. **Analytics**: Access system statistics and reports


### Migration
For database schema updates:
```bash
python migrate_vehicles.py
```

## File Structure

```
parking-system/
├── app.py                 # Main Flask application
├── functions.py           # Business logic functions
├── database.py           # Database schema and initialization
├── migrate_vehicles.py   # Database migration script
├── parking.db            # SQLite database
├── api_config.yml        # API configuration
├── README.md             # Project documentation
├── static/
│   └── styles.css        # Custom styling with Quicksand font
└── templates/            # HTML templates
    ├── components/       # Reusable template components
    └── *.html           # Page templates
```

## Configuration

The system uses `api_config.yml` for API endpoint configuration and database settings. Modify this file to adjust system behavior and API structure.

## Support

For technical issues or feature requests, refer to the code structure and documentation within the project files. The system is designed for easy customization and extension. 