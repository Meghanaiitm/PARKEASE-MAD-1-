# Database Design Documentation

## Overview
This document explains the database schema design, constraints, and the reasoning behind the architectural decisions for the parking management system.

## Database Schema Analysis

### 1. Users Table
```sql
CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phono TEXT UNIQUE NOT NULL,
    vehno TEXT UNIQUE NOT NULL,  
    password TEXT NOT NULL            
);
```

**Constraints & Design Decisions:**
- **PRIMARY KEY**: Auto-incrementing ID for unique user identification
- **UNIQUE email**: Prevents duplicate email registrations, but allows NULL (flexible registration)
- **UNIQUE phono**: Phone number must be unique across all users
- **UNIQUE vehno**: Vehicle number must be unique (one vehicle per user)
- **NOT NULL constraints**: Essential fields (name, phone, vehicle, password) cannot be empty

**Design Reasoning:**
- The original design assumes one vehicle per user (vehno in users table)
- This creates a limitation that was later addressed with the separate vehicles table
- Phone number uniqueness ensures no duplicate accounts per phone
- Email uniqueness with NULL allowance provides flexibility for registration

### 2. Vehicles Table
```sql
CREATE TABLE vehicles(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    vehicle_number TEXT NOT NULL,
    vehicle_type TEXT DEFAULT 'Car',
    vehicle_model TEXT,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, vehicle_number)
);
```

**Constraints & Design Decisions:**
- **FOREIGN KEY (user_id)**: Links vehicles to users, ensures referential integrity
- **UNIQUE(user_id, vehicle_number)**: Prevents duplicate vehicle numbers per user
- **DEFAULT 'Car'**: Assumes car as default vehicle type
- **is_primary BOOLEAN**: Allows designation of primary vehicle
- **created_at TIMESTAMP**: Tracks when vehicle was added

**Design Reasoning:**
- This table addresses the limitation of the original users table
- Allows multiple vehicles per user (many-to-one relationship)
- The unique constraint prevents users from adding the same vehicle twice
- Primary vehicle designation helps in booking workflows

### 3. Admin Table
```sql
CREATE TABLE admin(
    adminid INTEGER PRIMARY KEY,
    adminpass TEXT NOT NULL        
);
```

**Constraints & Design Decisions:**
- **Simple structure**: Minimal admin authentication
- **PRIMARY KEY**: Unique admin identification
- **NOT NULL password**: Ensures admin password is always set

**Design Reasoning:**
- Simplified admin management with single admin account
- Could be enhanced to support multiple admin users
- Basic security through password requirement

### 4. Parking Lot Table
```sql
CREATE TABLE parking_lot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,
    price REAL NOT NULL,
    area TEXT NOT NULL,
    pin_code TEXT NOT NULL,
    spots INTEGER NOT NULL
);
```

**Constraints & Design Decisions:**
- **PRIMARY KEY**: Auto-incrementing lot identification
- **REAL price**: Supports decimal pricing (e.g., $10.50)
- **NOT NULL constraints**: All fields are required for lot creation
- **spots INTEGER**: Tracks total capacity of the lot

**Design Reasoning:**
- Flexible location storage (could be enhanced with coordinates)
- Decimal pricing support for precise cost management
- Area and pin_code provide location context
- Spots field enables capacity management

### 5. Parking Spot Table
```sql
CREATE TABLE parking_spot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    spot_number TEXT,
    level TEXT, 
    status TEXT CHECK(status IN ('O', 'A')) NOT NULL DEFAULT 'A',
    FOREIGN KEY (lot_id) REFERENCES parking_lot(id)
);
```

**Constraints & Design Decisions:**
- **FOREIGN KEY (lot_id)**: Links spots to parking lots
- **CHECK constraint**: Status must be 'O' (Occupied) or 'A' (Available)
- **DEFAULT 'A'**: New spots start as available
- **TEXT spot_number**: Flexible spot identification (A1, B2, etc.)
- **TEXT level**: Supports multi-level parking structures

**Design Reasoning:**
- Hierarchical structure: Lot → Spots
- Simple status management with check constraint
- Flexible spot numbering system
- Multi-level parking support

### 6. Booking Table
```sql
CREATE TABLE booking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    spot_id INTEGER NOT NULL,
    vehicle_id INTEGER,
    status TEXT CHECK(status IN ('booked', 'completed', 'cancelled')) NOT NULL DEFAULT 'booked',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (spot_id) REFERENCES parking_spot(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);
```

**Constraints & Design Decisions:**
- **Multiple FOREIGN KEYS**: Links to users, spots, and vehicles
- **CHECK constraint**: Status must be 'booked', 'completed', or 'cancelled'
- **DEFAULT 'booked'**: New bookings start as booked
- **created_at TIMESTAMP**: Tracks booking creation time
- **Optional vehicle_id**: Allows booking without specific vehicle

**Design Reasoning:**
- Central booking entity connecting all major entities
- Comprehensive status tracking for booking lifecycle
- Timestamp for audit trails and reporting
- Optional vehicle linking provides flexibility

## Key Design Patterns

### 1. Referential Integrity
- All relationships use FOREIGN KEY constraints
- Ensures data consistency across tables
- Prevents orphaned records

### 2. Status Management
- Uses CHECK constraints for status validation
- Consistent status patterns across tables
- Default values for new records

### 3. Audit Trail
- Timestamp fields for tracking creation times
- Enables historical analysis and debugging

### 4. Flexibility vs. Structure
- TEXT fields for flexible data storage
- UNIQUE constraints where appropriate
- NULL allowances where flexibility is needed

## Potential Improvements

### 1. Data Validation
- Add more CHECK constraints for data validation
- Implement proper email format validation
- Add phone number format constraints

### 2. Enhanced Security
- Hash passwords instead of plain text storage
- Implement proper authentication mechanisms

### 3. Extended Functionality
- Add booking duration fields
- Implement pricing tiers
- Add payment tracking

### 4. Performance Optimization
- Add indexes on frequently queried fields
- Consider partitioning for large datasets

## Conclusion

The database design follows a logical structure with proper relationships and constraints. The use of FOREIGN KEYS ensures data integrity, while CHECK constraints maintain data quality. The design balances flexibility with structure, allowing for future enhancements while maintaining current functionality.

The schema supports a complete parking management workflow from user registration to booking completion, with proper audit trails and status tracking throughout the process. 