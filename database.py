import sqlite3

conn=sqlite3.connect("parking.db")
cur=conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email   TEXT UNIQUE,
    phono TEXT UNIQUE NOT NULL,
    vehno TEXT UNIQUE NOT NULL,  
    password  TEXT NOT NULL            
    );
""")

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

cur.execute("""
CREATE TABLE IF NOT EXISTS admin(
    adminid INTEGER PRIMARY KEY,
    adminpass TEXT NOT NULL        
    );
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS parking_lot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,
    price REAL NOT NULL,
    area TEXT NOT NULL,
    pin_code TEXT NOT NULL,
    spots INTEGER NOT NULL
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS parking_spot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lot_id INTEGER NOT NULL,
    spot_number TEXT,
    level TEXT, 
    status TEXT CHECK(status IN ('O', 'A')) NOT NULL DEFAULT 'A',
    FOREIGN KEY (lot_id) REFERENCES parking_lot(id)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS booking (
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
""")

conn.commit()
conn.close()
