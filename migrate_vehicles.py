#!/usr/bin/env python3
import sqlite3
import sys

def migrate_database():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    print("Starting vehicle migration...")
    
    try:
        # 1. Create vehicles table if it doesn't exist
        print("Creating vehicles table...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicles(
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
        """)
        
        # 2. Add vehicle_id and created_at columns to booking table if they don't exist
        print("Updating booking table...")
        
        # Check if vehicle_id column exists
        cur.execute("PRAGMA table_info(booking)")
        columns = [column[1] for column in cur.fetchall()]
        
        if 'vehicle_id' not in columns:
            print("Adding vehicle_id column to booking table...")
            cur.execute("ALTER TABLE booking ADD COLUMN vehicle_id INTEGER REFERENCES vehicles(id)")
        
        if 'created_at' not in columns:
            print("Adding created_at column to booking table...")
            cur.execute("ALTER TABLE booking ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        
        # 3. Get all users and create vehicle records for them
        print("Creating vehicle records for existing users...")
        cur.execute("SELECT id, vehno FROM users")
        users = cur.fetchall()
        
        for user_id, vehno in users:
            try:
                # Create primary vehicle for each user
                cur.execute("""
                INSERT INTO vehicles (user_id, vehicle_number, vehicle_type, is_primary)
                VALUES (?, ?, 'Car', 1)
                """, (user_id, vehno))
                print(f"Created vehicle record for user {user_id}: {vehno}")
            except sqlite3.IntegrityError:
                print(f"Vehicle record already exists for user {user_id}: {vehno}")
        
        # 4. Update existing bookings with vehicle information
        print("Updating existing bookings with vehicle information...")
        
        # Get all bookings without vehicle_id
        cur.execute("""
        SELECT b.id, b.user_id, v.id as vehicle_id
        FROM booking b
        JOIN vehicles v ON b.user_id = v.user_id AND v.is_primary = 1
        WHERE b.vehicle_id IS NULL
        """)
        
        bookings_to_update = cur.fetchall()
        
        for booking_id, user_id, vehicle_id in bookings_to_update:
            cur.execute("UPDATE booking SET vehicle_id = ? WHERE id = ?", (vehicle_id, booking_id))
            print(f"Updated booking {booking_id} with vehicle {vehicle_id}")
        
        # Commit all changes
        conn.commit()
        print("Migration completed successfully!")
        
        # 5. Show migration summary
        cur.execute("SELECT COUNT(*) FROM vehicles")
        vehicle_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM booking WHERE vehicle_id IS NOT NULL")
        booking_count = cur.fetchone()[0]
        
        print(f"\nMigration Summary:")
        print(f"- Total vehicles created: {vehicle_count}")
        print(f"- Total bookings updated: {booking_count}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 