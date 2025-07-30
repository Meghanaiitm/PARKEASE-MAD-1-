import sqlite3
import re
from datetime import datetime
import hashlib

def insert_user(name, email, phono, vehno, password):
    if not all([name, email, phono, vehno, password]):
        print("All fields are required.")
        return False
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        print("Invalid email format.")
        return False
    if not phono.isdigit() or len(phono) != 10:
        print("Phone number must be 10 digits.")
        return False

    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cur.execute("""
        INSERT INTO users (name, email, phono, vehno, password)
        VALUES (?, ?, ?, ?, ?)
        """, (name, email, phono, vehno, hashed_password))
        
        user_id = cur.lastrowid
        
        cur.execute("""
        INSERT INTO vehicles (user_id, vehicle_number, vehicle_type, is_primary)
        VALUES (?, ?, 'Car', 1)
        """, (user_id, vehno))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def update_user_name(phono, new_name):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = ? WHERE phono = ?", (new_name, phono))
    conn.commit()
    print("Name updated." if cur.rowcount else "User not found.")
    conn.close()

def update_user_email(phono, new_email):
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', new_email):
        print("Invalid email format.")
        return
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET email = ? WHERE phono = ?", (new_email, phono))
    conn.commit()
    print("Email updated." if cur.rowcount else "User not found.")
    conn.close()

def update_user_phone(old_phono, new_phono):
    if not new_phono.isdigit() or len(new_phono) != 10:
        print("Phone number must be 10 digits.")
        return
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET phono = ? WHERE phono = ?", (new_phono, old_phono))
    conn.commit()
    print("Phone number updated." if cur.rowcount else "User not found.")
    conn.close()

def update_user_vehicle_number(phono, new_vehno):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET vehno = ? WHERE phono = ?", (new_vehno, phono))
    conn.commit()
    print("Vehicle number updated." if cur.rowcount else "User not found.")
    conn.close()

def update_user_password(phono, new_password):
    if not new_password:
        print("Password cannot be empty.")
        return
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = ? WHERE phono = ?", (new_password, phono))
    conn.commit()
    print("Password updated." if cur.rowcount else "User not found.")
    conn.close()

def check_email_exists(email):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0

def login_user(email, password):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
    user = cur.fetchone()
    conn.close()
    if user :
        return True,user[0]
    return False,None

def insert_admin(adminid, adminpass):
    if not adminpass:
        print("Admin password cannot be empty.")
        return
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO admin (adminid, adminpass)
            VALUES (?, ?)
        """, (adminid, adminpass))
        conn.commit()
        print("Admin inserted successfully.")
    except sqlite3.IntegrityError as e:
        print("Error inserting admin:", e)
    finally:
        conn.close()


def login_admin(adminid, adminpass):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    try:
        adminid_int = int(adminid)
        cur.execute("""
            SELECT * FROM admin WHERE adminid = ? AND adminpass = ?
        """, (adminid_int, adminpass))
        admin = cur.fetchone()
        conn.close()
        return admin is not None
    except ValueError:
        conn.close()
        return False

def add_parking_lot(location, price, area, pin_code, spots):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO parking_lot (location, price, area, pin_code, spots)
            VALUES (?, ?, ?, ?, ?)
        """, (location, price, area, pin_code, spots))
        
        lot_id = cur.lastrowid
        
        for i in range(1, spots + 1):
            spot_number = f"{i:02d}"
            
            if i <= 5:
                level = "G"
            elif i <= 10:
                level = "1"
            else:
                level = "2"
            
            cur.execute("""
                INSERT INTO parking_spot (lot_id, spot_number, level, status)
                VALUES (?, ?, ?, 'A')
            """, (lot_id, spot_number, level))
        
        conn.commit()
        print(f"Parking lot '{location}' added with {spots} spots.")
    except sqlite3.IntegrityError as e:
        print("Error:", e)
    finally:
        conn.close()

def update_parking_lot_spots(lot_id, new_spots):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE parking_lot SET spots = ? WHERE id = ?", (new_spots, lot_id))
    conn.commit()
    print("Parking lot spot count updated." if cur.rowcount else "Lot not found.")
    conn.close()

def delete_parking_lot(lot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM parking_lot WHERE id = ?", (lot_id,))
    conn.commit()
    print("Parking lot deleted." if cur.rowcount else "Lot not found.")
    conn.close()

def get_all_parking_lots():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM parking_lot")
    lots = cur.fetchall()
    conn.close()
    return lots

def get_parking_lot_by_id(lot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM parking_lot WHERE id = ?", (lot_id,))
    lot = cur.fetchone()
    conn.close()
    return lot

def add_parking_spot(lot_id, spot_number, level):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO parking_spot (lot_id, spot_number, level, status)
        VALUES (?, ?, ?, 'A')
    """, (lot_id, spot_number, level))
    conn.commit()
    print("Parking spot added.")
    conn.close()

def delete_parking_spot(spot_id):
    try:
        conn = sqlite3.connect("parking.db")
        cur = conn.cursor()
        cur.execute("SELECT status, lot_id FROM parking_spot WHERE id = ?", (spot_id,))
        result = cur.fetchone()
        if not result:
            conn.close()
            return False
        if result[0] == 'O':
            conn.close()
            return False
        lot_id = result[1]
        cur.execute("DELETE FROM parking_spot WHERE id = ?", (spot_id,))
        cur.execute("UPDATE parking_lot SET spots = spots - 1 WHERE id = ? AND spots > 0", (lot_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting parking spot: {e}")
        return False

def get_spots_by_lot(lot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM parking_spot WHERE lot_id = ?", (lot_id,))
    spots = cur.fetchall()
    conn.close()
    return spots

def get_spots_by_lot_full(lot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT ps.id, ps.spot_number, ps.level,
               CASE WHEN b.id IS NOT NULL AND b.status = 'booked' THEN 'O' ELSE ps.status END as status
        FROM parking_spot ps
        LEFT JOIN booking b ON ps.id = b.spot_id AND b.status = 'booked'
        WHERE ps.lot_id = ?
        ORDER BY CAST(ps.spot_number AS INTEGER)
    """, (lot_id,))
    spots = cur.fetchall()
    conn.close()
    return spots

def get_available_spots(lot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM parking_spot
        WHERE lot_id = ? AND status = 'A'
    """, (lot_id,))
    spots = cur.fetchall()
    conn.close()
    return spots

def mark_spot_occupied(spot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE parking_spot SET status = 'O' WHERE id = ?", (spot_id,))
    conn.commit()
    conn.close()

def mark_spot_available(spot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE parking_spot SET status = 'A' WHERE id = ?", (spot_id,))
    conn.commit()
    conn.close()

def get_all_bookings():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM booking")
    bookings = cur.fetchall()
    conn.close()
    return bookings

def make_booking(user_id, spot_id, booking_time):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    try:
        cur.execute("""
        INSERT INTO booking (user_id, spot_id, status, created_at)
        VALUES (?, ?, 'booked', ?)
        """, (user_id, spot_id, booking_time))
        
        cur.execute("UPDATE parking_spot SET status = 'O' WHERE id = ?", (spot_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error making booking: {e}")
        conn.close()
        return False

def make_booking_with_vehicle(user_id, spot_id, vehicle_id, booking_time):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    try:
        cur.execute("""
        INSERT INTO booking (user_id, spot_id, vehicle_id, status, created_at)
        VALUES (?, ?, ?, 'booked', ?)
        """, (user_id, spot_id, vehicle_id, booking_time))
        
        cur.execute("UPDATE parking_spot SET status = 'O' WHERE id = ?", (spot_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error making booking: {e}")
        conn.close()
        return False

def cancel_booking(booking_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()

    cur.execute("SELECT spot_id FROM booking WHERE id = ?", (booking_id,))
    row = cur.fetchone()
    if not row:
        print("Booking not found.")
        conn.close()
        return

    spot_id = row[0]

    cur.execute("UPDATE booking SET status = 'cancelled' WHERE id = ?", (booking_id,))
    cur.execute("UPDATE parking_spot SET status = 'A' WHERE id = ?", (spot_id,))
    conn.commit()
    print("Booking cancelled and spot released.")
    conn.close()

def complete_booking(booking_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()

    cur.execute("SELECT spot_id FROM booking WHERE id = ?", (booking_id,))
    row = cur.fetchone()
    if not row:
        print("Booking not found.")
        conn.close()
        return

    spot_id = row[0]

    cur.execute("UPDATE booking SET status = 'completed' WHERE id = ?", (booking_id,))
    cur.execute("UPDATE parking_spot SET status = 'A' WHERE id = ?", (spot_id,))
    conn.commit()
    print("Booking completed.")
    conn.close()

def get_user_bookings(user_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM booking WHERE user_id = ?", (user_id,))
    bookings = cur.fetchall()
    conn.close()
    return bookings

def get_user_by_id(user_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def get_current_bookings(user_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT b.id, b.user_id, ps.spot_number, b.status, b.created_at, pl.location, pl.price, v.vehicle_number, v.vehicle_type
    FROM booking b
    JOIN parking_spot ps ON b.spot_id = ps.id
    JOIN parking_lot pl ON ps.lot_id = pl.id
    LEFT JOIN vehicles v ON b.vehicle_id = v.id
    WHERE b.user_id = ? AND b.status = 'booked'
    ORDER BY b.created_at DESC
    """, (user_id,))
    
    bookings = cur.fetchall()
    conn.close()
    return bookings

def get_previous_bookings(user_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT b.id, b.user_id, ps.spot_number, b.status, b.created_at, pl.location, pl.price, v.vehicle_number, v.vehicle_type
    FROM booking b
    JOIN parking_spot ps ON b.spot_id = ps.id
    JOIN parking_lot pl ON ps.lot_id = pl.id
    LEFT JOIN vehicles v ON b.vehicle_id = v.id
    WHERE b.user_id = ? AND b.status IN ('completed', 'cancelled')
    ORDER BY b.created_at DESC
    """, (user_id,))
    
    bookings = cur.fetchall()
    conn.close()
    return bookings

def cancel_booking_by_id(booking_id):
    try:
        conn = sqlite3.connect("parking.db")
        cur = conn.cursor()

        cur.execute("SELECT spot_id FROM booking WHERE id = ?", (booking_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False

        spot_id = row[0]

        cur.execute("UPDATE booking SET status = 'cancelled' WHERE id = ?", (booking_id,))
        cur.execute("UPDATE parking_spot SET status = 'A' WHERE id = ?", (spot_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error cancelling booking: {e}")
        return False

def complete_booking_by_id(booking_id):
    try:
        conn = sqlite3.connect("parking.db")
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(booking)")
        columns = [col[1] for col in cur.fetchall()]
        if 'completed_at' not in columns:
            cur.execute("ALTER TABLE booking ADD COLUMN completed_at TIMESTAMP")
        
        cur.execute("SELECT spot_id FROM booking WHERE id = ?", (booking_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False
        spot_id = row[0]
        completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("UPDATE booking SET status = 'completed', completed_at = ? WHERE id = ?", (completed_at, booking_id))
        cur.execute("UPDATE parking_spot SET status = 'A' WHERE id = ?", (spot_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error completing booking: {e}")
        return False

def update_user_name_by_id(user_id, new_name):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
    conn.commit()
    conn.close()

def update_user_email_by_id(user_id, new_email):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    conn.commit()
    conn.close()

def update_user_vehicle_number_by_id(user_id, new_vehno):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET vehno = ? WHERE id = ?", (new_vehno, user_id))
    conn.commit()
    conn.close()

def get_booking_details(booking_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, b.user_id, ps.spot_number, b.status, pl.location, pl.price, pl.area, b.created_at, b.completed_at, v.vehicle_number, v.vehicle_type
        FROM booking b
        JOIN parking_spot ps ON b.spot_id = ps.id
        JOIN parking_lot pl ON ps.lot_id = pl.id
        LEFT JOIN vehicles v ON b.vehicle_id = v.id
        WHERE b.id = ?
    """, (booking_id,))
    booking = cur.fetchone()
    conn.close()
    return booking

def get_parking_lot_spots_with_status(lot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT ps.id, ps.spot_number, ps.level, ps.status, pl.location, pl.price
        FROM parking_spot ps
        JOIN parking_lot pl ON ps.lot_id = pl.id
        WHERE ps.lot_id = ?
        ORDER BY ps.spot_number
    """, (lot_id,))
    spots = cur.fetchall()
    conn.close()
    return spots

def get_admin_spot_details(spot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT ps.id, ps.spot_number, ps.status, pl.location, pl.price,
               b.id as booking_id, b.user_id, u.vehno, b.created_at
        FROM parking_spot ps
        JOIN parking_lot pl ON ps.lot_id = pl.id
        LEFT JOIN booking b ON ps.id = b.spot_id AND b.status = 'booked'
        LEFT JOIN users u ON b.user_id = u.id
        WHERE ps.id = ?
    """, (spot_id,))
    details = cur.fetchone()
    conn.close()
    return details

def get_total_users_count():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_total_parking_lots_count():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM parking_lot")
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_today_bookings_count():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM booking WHERE status IN ('booked', 'completed')")
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_total_bookings_count():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM booking")
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_active_bookings_count():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM booking WHERE status = 'booked'")
    count = cur.fetchone()[0]
    conn.close()
    return count

def get_parking_lots_with_occupancy():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT pl.id, pl.location, pl.price, pl.area, pl.pin_code, pl.spots,
               SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) as occupied_spots,
               SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) as available_spots
        FROM parking_lot pl
        LEFT JOIN parking_spot ps ON pl.id = ps.lot_id
        GROUP BY pl.id
        ORDER BY pl.id
    """)
    lots = cur.fetchall()
    lots_with_occupancy = []
    for lot in lots:
        total_spots = lot[5]
        occupied_spots = lot[6] or 0
        available_spots = lot[7] or 0
        lots_with_occupancy.append(lot[:6] + (total_spots, occupied_spots, available_spots))
    conn.close()
    return lots_with_occupancy

def get_recent_users(limit=10):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT ?", (limit,))
    users = cur.fetchall()
    conn.close()
    return users

def get_recent_bookings(limit=10):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, b.user_id, u.name, u.vehno, ps.spot_number, pl.location, b.status
        FROM booking b
        JOIN users u ON b.user_id = u.id
        JOIN parking_spot ps ON b.spot_id = ps.id
        JOIN parking_lot pl ON ps.lot_id = pl.id
        ORDER BY b.id DESC LIMIT ?
    """, (limit,))
    bookings = cur.fetchall()
    conn.close()
    return bookings

def get_all_users():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY id DESC")
    users = cur.fetchall()
    conn.close()
    return users

def get_all_parking_lots_with_spots():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT pl.*, 
               COUNT(ps.id) as total_spots,
               SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) as occupied_spots,
               SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) as available_spots
        FROM parking_lot pl
        LEFT JOIN parking_spot ps ON pl.id = ps.lot_id
        GROUP BY pl.id
        ORDER BY pl.id
    """)
    lots = cur.fetchall()
    conn.close()
    return lots

def update_parking_lot(lot_id, location, price, area, pin_code, spots):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("SELECT spots FROM parking_lot WHERE id = ?", (lot_id,))
    result = cur.fetchone()
    if not result:
        conn.close()
        return False
    current_spots = result[0]
    
    cur.execute("""
        SELECT ps.spot_number, ps.id, b.id as booking_id, b.user_id, b.status as booking_status, b.created_at
        FROM parking_spot ps
        LEFT JOIN booking b ON ps.id = b.spot_id AND b.status = 'booked'
        WHERE ps.lot_id = ? AND ps.status = 'O'
        ORDER BY CAST(ps.spot_number AS INTEGER)
    """, (lot_id,))
    occupied_spots_info = cur.fetchall()
    
    cur.execute("""
        UPDATE parking_lot 
        SET location = ?, price = ?, area = ?, pin_code = ?, spots = ?
        WHERE id = ?
    """, (location, price, area, pin_code, spots, lot_id))
    
    if spots != current_spots:
        booking_mapping = {}
        occupied_spot_numbers = []
        for spot_info in occupied_spots_info:
            spot_number = int(spot_info[0])
            old_spot_id = spot_info[1]
            booking_id = spot_info[2]
            user_id = spot_info[3]
            booking_status = spot_info[4]
            created_at = spot_info[5]
            occupied_spot_numbers.append(spot_number)
            booking_mapping[spot_number] = {
                'booking_id': booking_id,
                'user_id': user_id,
                'booking_status': booking_status,
                'created_at': created_at
            }
        
        cur.execute("DELETE FROM parking_spot WHERE lot_id = ?", (lot_id,))
        
        occupied_count = len(occupied_spot_numbers)
        
        if spots < occupied_count:
            spots_to_create = occupied_count
            print(f"⚠️  Warning: Requested {spots} spots but {occupied_count} are occupied. Keeping {occupied_count} spots.")
        else:
            spots_to_create = spots
        
        spots_created = 0
        
        for spot_number in sorted(occupied_spot_numbers):
            cur.execute("""
                INSERT INTO parking_spot (lot_id, spot_number, level, status)
                VALUES (?, ?, ?, ?)
            """, (lot_id, str(spot_number), 1, 'O'))
            
            new_spot_id = cur.lastrowid
            if spot_number in booking_mapping:
                booking_info = booking_mapping[spot_number]
                if booking_info['booking_id']:
                    cur.execute("""
                        INSERT INTO booking (user_id, spot_id, status, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (booking_info['user_id'], new_spot_id, booking_info['booking_status'], 
                          booking_info['created_at']))
            spots_created += 1
        
        if spots_created < spots_to_create:
            for i in range(1, spots_to_create + 1):
                if i not in occupied_spot_numbers:
                    cur.execute("""
                        INSERT INTO parking_spot (lot_id, spot_number, level, status)
                        VALUES (?, ?, ?, ?)
                    """, (lot_id, str(i), 1, 'A'))
                    spots_created += 1
                    
                    if spots_created >= spots_to_create:
                        break
    
    conn.commit()
    conn.close()
    return True

def sync_parking_lot_spots(lot_id, current_spots):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM parking_spot 
        WHERE lot_id = ? AND spot_number > ? AND status = 'A'
    """, (lot_id, current_spots))
    conn.commit()
    conn.close()

def search_users(query):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.name, u.email, u.phono, u.vehno, COUNT(v.id) as vehicle_count
        FROM users u
        LEFT JOIN vehicles v ON u.id = v.user_id
        WHERE u.name LIKE ? OR u.email LIKE ? OR u.phono LIKE ? OR u.vehno LIKE ?
        GROUP BY u.id, u.name, u.email, u.phono, u.vehno
        ORDER BY u.name
    """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    users = cur.fetchall()
    conn.close()
    return users

def search_parking_lots(query):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM parking_lot 
        WHERE location LIKE ? OR area LIKE ? OR pin_code LIKE ?
        ORDER BY id DESC
    """, (f'%{query}%', f'%{query}%', f'%{query}%'))
    lots = cur.fetchall()
    conn.close()
    return lots

def search_bookings(query):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, b.user_id, u.name, v.vehicle_number, v.vehicle_type, ps.spot_number, pl.location, b.status, b.created_at
        FROM booking b
        JOIN users u ON b.user_id = u.id
        JOIN parking_spot ps ON b.spot_id = ps.id
        JOIN parking_lot pl ON ps.lot_id = pl.id
        LEFT JOIN vehicles v ON b.vehicle_id = v.id
        WHERE u.name LIKE ? OR v.vehicle_number LIKE ? OR pl.location LIKE ? OR ps.spot_number LIKE ?
        ORDER BY b.created_at DESC
    """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    bookings = cur.fetchall()
    conn.close()
    return bookings

def search_users_by_category(query, category):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    if category == "all":
        cur.execute("""
            SELECT u.id, u.name, u.email, u.phono, u.vehno, COUNT(v.id) as vehicle_count
            FROM users u
            LEFT JOIN vehicles v ON u.id = v.user_id
            WHERE u.name LIKE ? OR u.email LIKE ? OR u.phono LIKE ? OR u.vehno LIKE ?
            GROUP BY u.id, u.name, u.email, u.phono, u.vehno
            ORDER BY u.name
        """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    elif category == "name":
        cur.execute("""
            SELECT u.id, u.name, u.email, u.phono, u.vehno, COUNT(v.id) as vehicle_count
            FROM users u
            LEFT JOIN vehicles v ON u.id = v.user_id
            WHERE u.name LIKE ?
            GROUP BY u.id, u.name, u.email, u.phono, u.vehno
            ORDER BY u.name
        """, (f'%{query}%',))
    elif category == "email":
        cur.execute("""
            SELECT u.id, u.name, u.email, u.phono, u.vehno, COUNT(v.id) as vehicle_count
            FROM users u
            LEFT JOIN vehicles v ON u.id = v.user_id
            WHERE u.email LIKE ?
            GROUP BY u.id, u.name, u.email, u.phono, u.vehno
            ORDER BY u.name
        """, (f'%{query}%',))
    elif category == "phone":
        cur.execute("""
            SELECT u.id, u.name, u.email, u.phono, u.vehno, COUNT(v.id) as vehicle_count
            FROM users u
            LEFT JOIN vehicles v ON u.id = v.user_id
            WHERE u.phono LIKE ?
            GROUP BY u.id, u.name, u.email, u.phono, u.vehno
            ORDER BY u.name
        """, (f'%{query}%',))
    elif category == "vehicle":
        cur.execute("""
            SELECT u.id, u.name, u.email, u.phono, u.vehno, COUNT(v.id) as vehicle_count
            FROM users u
            LEFT JOIN vehicles v ON u.id = v.user_id
            WHERE u.vehno LIKE ?
            GROUP BY u.id, u.name, u.email, u.phono, u.vehno
            ORDER BY u.name
        """, (f'%{query}%',))
    elif category == "id":
        cur.execute("""
            SELECT u.id, u.name, u.email, u.phono, u.vehno, COUNT(v.id) as vehicle_count
            FROM users u
            LEFT JOIN vehicles v ON u.id = v.user_id
            WHERE u.id = ?
            GROUP BY u.id, u.name, u.email, u.phono, u.vehno
            ORDER BY u.name
        """, (query,))
    
    users = cur.fetchall()
    conn.close()
    return users

def search_parking_lots_by_category(query, category):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    base_query = """
        SELECT pl.*, 
               COUNT(ps.id) as total_spots,
               SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) as occupied_spots
        FROM parking_lot pl
        LEFT JOIN parking_spot ps ON pl.id = ps.lot_id
        WHERE {condition}
        GROUP BY pl.id
        ORDER BY pl.id DESC
    """
    
    if category == "all":
        cur.execute(base_query.format(condition="pl.location LIKE ? OR pl.area LIKE ? OR pl.pin_code LIKE ?"),
                   (f'%{query}%', f'%{query}%', f'%{query}%'))
    elif category == "location":
        cur.execute(base_query.format(condition="pl.location LIKE ?"),
                   (f'%{query}%',))
    elif category == "area":
        cur.execute(base_query.format(condition="pl.area LIKE ?"),
                   (f'%{query}%',))
    elif category == "pin_code":
        cur.execute(base_query.format(condition="pl.pin_code LIKE ?"),
                   (f'%{query}%',))
    elif category == "price":
        cur.execute(base_query.format(condition="pl.price = ?"),
                   (query,))
    elif category == "lot_id":
        cur.execute(base_query.format(condition="pl.id = ?"),
                   (query,))
    
    lots = cur.fetchall()
    conn.close()
    return lots

def search_bookings_by_category(query, category):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    if category == "all":
        cur.execute("""
            SELECT b.id, b.user_id, u.name, v.vehicle_number, v.vehicle_type, ps.spot_number, pl.location, b.status, b.created_at
            FROM booking b
            JOIN users u ON b.user_id = u.id
            JOIN parking_spot ps ON b.spot_id = ps.id
            JOIN parking_lot pl ON ps.lot_id = pl.id
            LEFT JOIN vehicles v ON b.vehicle_id = v.id
            WHERE u.name LIKE ? OR v.vehicle_number LIKE ? OR pl.location LIKE ? OR ps.spot_number LIKE ?
            ORDER BY b.created_at DESC
        """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    elif category == "booking_id":
        cur.execute("""
            SELECT b.id, b.user_id, u.name, v.vehicle_number, v.vehicle_type, ps.spot_number, pl.location, b.status, b.created_at
            FROM booking b
            JOIN users u ON b.user_id = u.id
            JOIN parking_spot ps ON b.spot_id = ps.id
            JOIN parking_lot pl ON ps.lot_id = pl.id
            LEFT JOIN vehicles v ON b.vehicle_id = v.id
            WHERE b.id = ?
            ORDER BY b.created_at DESC
        """, (query,))
    elif category == "user_name":
        cur.execute("""
            SELECT b.id, b.user_id, u.name, v.vehicle_number, v.vehicle_type, ps.spot_number, pl.location, b.status, b.created_at
            FROM booking b
            JOIN users u ON b.user_id = u.id
            JOIN parking_spot ps ON b.spot_id = ps.id
            JOIN parking_lot pl ON ps.lot_id = pl.id
            LEFT JOIN vehicles v ON b.vehicle_id = v.id
            WHERE u.name LIKE ?
            ORDER BY b.created_at DESC
        """, (f'%{query}%',))
    elif category == "vehicle_number":
        cur.execute("""
            SELECT b.id, b.user_id, u.name, v.vehicle_number, v.vehicle_type, ps.spot_number, pl.location, b.status, b.created_at
            FROM booking b
            JOIN users u ON b.user_id = u.id
            JOIN parking_spot ps ON b.spot_id = ps.id
            JOIN parking_lot pl ON ps.lot_id = pl.id
            LEFT JOIN vehicles v ON b.vehicle_id = v.id
            WHERE v.vehicle_number LIKE ?
            ORDER BY b.created_at DESC
        """, (f'%{query}%',))
    elif category == "spot_number":
        cur.execute("""
            SELECT b.id, b.user_id, u.name, v.vehicle_number, v.vehicle_type, ps.spot_number, pl.location, b.status, b.created_at
            FROM booking b
            JOIN users u ON b.user_id = u.id
            JOIN parking_spot ps ON b.spot_id = ps.id
            JOIN parking_lot pl ON ps.lot_id = pl.id
            LEFT JOIN vehicles v ON b.vehicle_id = v.id
            WHERE ps.spot_number LIKE ?
            ORDER BY b.created_at DESC
        """, (f'%{query}%',))
    elif category == "location":
        cur.execute("""
            SELECT b.id, b.user_id, u.name, v.vehicle_number, v.vehicle_type, ps.spot_number, pl.location, b.status, b.created_at
            FROM booking b
            JOIN users u ON b.user_id = u.id
            JOIN parking_spot ps ON b.spot_id = ps.id
            JOIN parking_lot pl ON ps.lot_id = pl.id
            LEFT JOIN vehicles v ON b.vehicle_id = v.id
            WHERE pl.location LIKE ?
            ORDER BY b.created_at DESC
        """, (f'%{query}%',))
    elif category == "status":
        cur.execute("""
            SELECT b.id, b.user_id, u.name, v.vehicle_number, v.vehicle_type, ps.spot_number, pl.location, b.status, b.created_at
            FROM booking b
            JOIN users u ON b.user_id = u.id
            JOIN parking_spot ps ON b.spot_id = ps.id
            JOIN parking_lot pl ON ps.lot_id = pl.id
            LEFT JOIN vehicles v ON b.vehicle_id = v.id
            WHERE b.status LIKE ?
            ORDER BY b.created_at DESC
        """, (f'%{query}%',))
    
    bookings = cur.fetchall()
    conn.close()
    return bookings

def get_revenue_by_parking_lot():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT pl.location, pl.price, COUNT(b.id) as total_bookings,
               (pl.price * COUNT(b.id)) as total_revenue
        FROM parking_lot pl
        LEFT JOIN parking_spot ps ON pl.id = ps.lot_id
        LEFT JOIN booking b ON ps.id = b.spot_id AND b.status = 'completed'
        GROUP BY pl.id
        ORDER BY total_revenue DESC
    """)
    revenue = cur.fetchall()
    conn.close()
    return revenue

def get_occupancy_by_parking_lot():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT pl.location, 
               COUNT(ps.id) as total_spots,
               SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) as occupied_spots,
               SUM(CASE WHEN ps.status = 'A' THEN 1 ELSE 0 END) as available_spots
        FROM parking_lot pl
        LEFT JOIN parking_spot ps ON pl.id = ps.lot_id
        GROUP BY pl.id
        ORDER BY pl.id
    """)
    occupancy = cur.fetchall()
    conn.close()
    return occupancy

def get_bookings_by_month():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%Y-%m', 'now') as month, COUNT(*) as bookings
        FROM booking
        WHERE status IN ('booked', 'completed')
    """)
    bookings = cur.fetchall()
    conn.close()
    return bookings

def get_spot_details_with_booking(spot_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT ps.id, ps.spot_number, ps.level, ps.status, pl.location, pl.price,
               b.id as booking_id, b.status as booking_status,
               u.name, u.vehno, u.phono
        FROM parking_spot ps
        JOIN parking_lot pl ON ps.lot_id = pl.id
        LEFT JOIN booking b ON ps.id = b.spot_id AND b.status = 'booked'
        LEFT JOIN users u ON b.user_id = u.id
        WHERE ps.id = ?
    """, (spot_id,))
    details = cur.fetchone()
    conn.close()
    return details

def add_revenue(amount):
    import datetime
    with open('revenue_debug.log', 'a') as f:
        f.write(f"[{datetime.datetime.now()}] add_revenue called with amount: {amount}\n")
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS revenue (id INTEGER PRIMARY KEY, total REAL)")
    cur.execute("SELECT total FROM revenue WHERE id = 1")
    row = cur.fetchone()
    if row:
        cur.execute("UPDATE revenue SET total = total + ? WHERE id = 1", (amount,))
    else:
        cur.execute("INSERT INTO revenue (id, total) VALUES (1, ?)", (amount,))
    conn.commit()
    conn.close()

def get_total_revenue():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS revenue (id INTEGER PRIMARY KEY, total REAL)")
    cur.execute("SELECT total FROM revenue WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def get_user_bookings_by_date(user_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT substr(b.created_at, 1, 10) as date, COUNT(*)
    FROM booking b
    WHERE b.user_id = ?
    GROUP BY date
    ORDER BY date
    """, (user_id,))
    
    data = cur.fetchall()
    conn.close()
    return data

def get_user_bookings_by_slot(user_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT ps.spot_number, COUNT(*)
    FROM booking b
    JOIN parking_spot ps ON b.spot_id = ps.id
    WHERE b.user_id = ?
    GROUP BY ps.spot_number
    ORDER BY ps.spot_number
    """, (user_id,))
    
    data = cur.fetchall()
    conn.close()
    return data

def add_vehicle(user_id, vehicle_number, vehicle_type="Car", vehicle_model=None):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    try:
        cur.execute("""
        INSERT INTO vehicles (user_id, vehicle_number, vehicle_type, vehicle_model)
        VALUES (?, ?, ?, ?)
        """, (user_id, vehicle_number, vehicle_type, vehicle_model))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_user_vehicles(user_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT id, vehicle_number, vehicle_type, vehicle_model, is_primary, created_at
    FROM vehicles
    WHERE user_id = ?
    ORDER BY is_primary DESC, created_at ASC
    """, (user_id,))
    
    vehicles = cur.fetchall()
    conn.close()
    return vehicles

def get_vehicle_by_id(vehicle_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT id, user_id, vehicle_number, vehicle_type, vehicle_model, is_primary, created_at
    FROM vehicles
    WHERE id = ?
    """, (vehicle_id,))
    
    vehicle = cur.fetchone()
    conn.close()
    return vehicle

def update_vehicle(vehicle_id, vehicle_number, vehicle_type, vehicle_model):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    try:
        cur.execute("""
        UPDATE vehicles 
        SET vehicle_number = ?, vehicle_type = ?, vehicle_model = ?
        WHERE id = ?
        """, (vehicle_number, vehicle_type, vehicle_model, vehicle_id))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def delete_vehicle(vehicle_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM booking WHERE vehicle_id = ?", (vehicle_id,))
    booking_count = cur.fetchone()[0]
    
    if booking_count > 0:
        conn.close()
        return False
    
    cur.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    conn.commit()
    conn.close()
    return True

def set_primary_vehicle(user_id, vehicle_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("UPDATE vehicles SET is_primary = 0 WHERE user_id = ?", (user_id,))
    
    cur.execute("UPDATE vehicles SET is_primary = 1 WHERE id = ? AND user_id = ?", (vehicle_id, user_id))
    
    conn.commit()
    conn.close()
    return True

def get_primary_vehicle(user_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT id, vehicle_number, vehicle_type, vehicle_model
    FROM vehicles
    WHERE user_id = ? AND is_primary = 1
    """, (user_id,))
    
    vehicle = cur.fetchone()
    conn.close()
    return vehicle

def get_user_bookings_by_vehicle(user_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT v.vehicle_number, v.vehicle_type, COUNT(b.id) as booking_count
    FROM vehicles v
    LEFT JOIN booking b ON v.id = b.vehicle_id
    WHERE v.user_id = ?
    GROUP BY v.id, v.vehicle_number, v.vehicle_type
    ORDER BY booking_count DESC
    """, (user_id,))
    
    data = cur.fetchall()
    conn.close()
    return data

def get_vehicle_booking_history(vehicle_id):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT b.id, b.created_at, b.status, ps.spot_number, pl.location
    FROM booking b
    JOIN parking_spot ps ON b.spot_id = ps.id
    JOIN parking_lot pl ON ps.lot_id = pl.id
    WHERE b.vehicle_id = ?
    ORDER BY b.created_at DESC
    """, (vehicle_id,))
    
    history = cur.fetchall()
    conn.close()
    return history

def get_all_users_with_vehicle_count():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    cur.execute("""
    SELECT u.id, u.name, u.email, u.phono, u.vehno, COUNT(v.id) as vehicle_count
    FROM users u
    LEFT JOIN vehicles v ON u.id = v.user_id
    GROUP BY u.id, u.name, u.email, u.phono, u.vehno
    ORDER BY u.name
    """)
    
    users = cur.fetchall()
    conn.close()
    return users

def search_parking_lots_for_users(query, category, price_filter=None, user_id=None):
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    
    base_query = """
        SELECT pl.*, 
               COUNT(ps.id) as total_spots,
               SUM(CASE WHEN ps.status = 'O' THEN 1 ELSE 0 END) as occupied_spots
        FROM parking_lot pl
        LEFT JOIN parking_spot ps ON pl.id = ps.lot_id
        WHERE {condition}
        GROUP BY pl.id
        ORDER BY pl.id DESC
    """
    
    if category == "all":
        condition = "pl.location LIKE ? OR pl.area LIKE ? OR pl.pin_code LIKE ?"
        params = (f'%{query}%', f'%{query}%', f'%{query}%')
    elif category == "location":
        condition = "pl.location LIKE ?"
        params = (f'%{query}%',)
    elif category == "pin_code":
        condition = "pl.pin_code LIKE ?"
        params = (f'%{query}%',)
    elif category == "previously_booked":
        if user_id:
            condition = """
                pl.id IN (
                    SELECT DISTINCT pl2.id 
                    FROM parking_lot pl2 
                    JOIN parking_spot ps2 ON pl2.id = ps2.lot_id 
                    JOIN booking b ON ps2.id = b.spot_id 
                    WHERE b.user_id = ?
                )
            """
            params = (user_id,)
        else:
            condition = "1=0"
            params = ()
    else:
        condition = "1=1"
        params = ()
    
    if price_filter:
        if condition != "1=1" and condition != "1=0":
            condition += " AND pl.price <= ?"
        else:
            condition = "pl.price <= ?"
        params = params + (price_filter,)
    
    cur.execute(base_query.format(condition=condition), params)
    lots = cur.fetchall()
    conn.close()
    return lots

def get_total_parking_lots_count():
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM parking_lot")
    count = cur.fetchone()[0]
    conn.close()
    return count

