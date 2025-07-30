from flask import Flask, request, jsonify, redirect, render_template, url_for, session, flash, make_response
from datetime import datetime, timedelta
from functions import *
import os

app = Flask(__name__)
app.secret_key = "banana_icecream_42"

# Disable caching for development


# -------- User Routes --------

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        data = request.form
        email = data["email"]
        password = data["password"]
        if email == "admin@123" and password == "321":
            session["admin_id"] = email
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            success, user_id = login_user(email, password)
            if success:
                session["user_id"] = user_id
                flash("Login successful!", "success")
                return redirect(url_for("user_dashboard"))
            else:
                flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/user/register", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        data = request.form
        name = data["name"].strip()
        email = data["email"].strip().lower()
        phone = data["phono"].strip()
        vehicle = data["vehno"].strip()
        password = data["password"]
        
        # Validation
        import re
        
        # Name validation
        if len(name) < 3:
            flash("Name must be at least 3 letters long.", "error")
            return render_template("register.html")
        
        if not re.match(r'^[A-Za-z\s]+$', name):
            flash("Name can only contain letters and spaces.", "error")
            return render_template("register.html")
        
        # Email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash("Please enter a valid email address.", "error")
            return render_template("register.html")
        
        # Phone validation
        if not re.match(r'^\d{10}$', phone):
            flash("Phone number must be exactly 10 digits.", "error")
            return render_template("register.html")
        
        # Check if email already exists
        from functions import check_email_exists
        if check_email_exists(email):
            flash("Email address already registered. Please use a different email.", "error")
            return render_template("register.html")
        
        # Insert user
        insert_user(name, email, phone, vehicle, password)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("user_login"))  
    return render_template("register.html") 

@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        data = request.form
        email = data["email"]
        password = data["password"]
        
        success, user_id = login_user(email, password)

        if success:
            session["user_id"] = user_id
            flash("Login successful!", "success")
            return redirect(url_for("user_dashboard"))
        else:
            flash("Invalid email or password.", "error")
    
    return render_template("login.html")

@app.route("/user/logout")
def user_logout():
    session.pop("user_id", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("index"))

@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    user_id = session["user_id"]
    from functions import get_user_by_id, get_current_bookings, get_previous_bookings, get_all_parking_lots, get_user_vehicles
    user_info = get_user_by_id(user_id)
    current_bookings = get_current_bookings(user_id)
    previous_bookings = get_previous_bookings(user_id)
    parking_lots = get_all_parking_lots()
    vehicles = get_user_vehicles(user_id)
    
    # Calculate booking statistics
    total_bookings = len(current_bookings) + len(previous_bookings)
    active_bookings = len([b for b in current_bookings if b[3] == 'booked'])
    completed_bookings = len([b for b in previous_bookings if b[3] == 'completed'])
    cancelled_bookings = len([b for b in previous_bookings if b[3] == 'cancelled'])
    
    return render_template("dashboard.html", 
                         user_info=user_info,
                         current_bookings=current_bookings,
                         previous_bookings=previous_bookings,
                         parking_lots=parking_lots,
                         vehicles=vehicles,
                         total_bookings=total_bookings,
                         active_bookings=active_bookings,
                         completed_bookings=completed_bookings,
                         cancelled_bookings=cancelled_bookings)

@app.route("/user/book_spot", methods=["POST"])
def book_spot():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    user_id = session["user_id"]
    lot_id = request.form.get("lot_id")
    spot_id = request.form.get("spot_id")
    vehicle_id = request.form.get("vehicle_id")
    booking_time = request.form.get("booking_time")
    
    # If booking_time is not provided, use current time
    if not booking_time:
        from datetime import datetime
        booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if not lot_id or not spot_id or not vehicle_id:
        flash("Please select parking lot, spot, and vehicle.", "error")
        return redirect(url_for("user_search"))
    
    # Verify the vehicle belongs to the current user
    from functions import get_vehicle_by_id, make_booking_with_vehicle
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or vehicle[1] != user_id:
        flash("Invalid vehicle selection.", "error")
        return redirect(url_for("user_search"))
    
    # Make the booking
    success = make_booking_with_vehicle(user_id, spot_id, vehicle_id, booking_time)
    if success:
        flash("Spot booked successfully!", "success")
    else:
        flash("Failed to book spot. Please try again.", "error")
    
    return redirect(url_for("user_dashboard"))

@app.route("/user/cancel_booking", methods=["POST"])
def cancel_booking():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    booking_id = request.form.get("booking_id")
    if booking_id:
        success = cancel_booking_by_id(booking_id)
        if success:
            flash("Booking cancelled successfully!", "success")
        else:
            flash("Failed to cancel booking.", "error")
    
    return redirect(url_for("user_dashboard"))

@app.route("/user/complete_booking", methods=["POST"])
def complete_booking():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    booking_id = request.form.get("booking_id")
    if booking_id:
        success = complete_booking_by_id(booking_id)
        if success:
            flash("Booking completed successfully!", "success")
        else:
            flash("Failed to complete booking.", "error")
    
    return redirect(url_for("user_dashboard"))

@app.route("/user/release_booking", methods=["POST"])
def release_booking():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    booking_id = request.form.get("booking_id")
    parking_time = request.form.get("parking_time")  # from database, pre-filled in modal
    releasing_time = request.form.get("releasing_time")  # from user device
    price_per_hour = float(request.form.get("price_per_hour"))
    from datetime import datetime
    start = datetime.strptime(parking_time, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(releasing_time, '%Y-%m-%d %H:%M:%S')
    hours = (end - start).total_seconds() / 3600
    hours = max(1, int(hours) if hours == int(hours) else int(hours) + 1)  # round up to next hour
    total_cost = price_per_hour * hours
    from functions import complete_booking_by_id, add_revenue
    complete_booking_by_id(booking_id)
    add_revenue(total_cost)
    flash(f"Spot released! Total cost: ₹{total_cost:.2f}", "success")
    return redirect(url_for("user_dashboard"))

@app.route("/user/profile")
def user_profile():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    user_id = session["user_id"]
    from functions import get_user_by_id, get_user_vehicles
    user_info = get_user_by_id(user_id)
    vehicles = get_user_vehicles(user_id)
    
    return render_template("profile.html", user_info=user_info, vehicles=vehicles)

@app.route("/user/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    user_id = session["user_id"]
    data = request.form
    
    # Update user information
    update_user_name_by_id(user_id, data["name"])
    update_user_email_by_id(user_id, data["email"])
    update_user_vehicle_number_by_id(user_id, data["vehno"])
    
    flash("Profile updated successfully!", "success")
    return redirect(url_for("user_profile"))

@app.route("/user/change_password", methods=["POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    user_id = session["user_id"]
    data = request.form
    
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")
    
    # Get user info to check current password
    user_info = get_user_by_id(user_id)
    if not user_info:
        flash("User not found!", "error")
        return redirect(url_for("user_profile"))
    
    # Validate current password
    if current_password != user_info[5]:  # user_info[5] is the password
        flash("Current password is incorrect!", "error")
        return redirect(url_for("user_profile"))
    
    # Validate new password
    if not new_password or len(new_password) < 6:
        flash("New password must be at least 6 characters long!", "error")
        return redirect(url_for("user_profile"))
    
    # Confirm password match
    if new_password != confirm_password:
        flash("New passwords do not match!", "error")
        return redirect(url_for("user_profile"))
    
    # Update password
    update_user_password(user_info[3], new_password)  # user_info[3] is the phone number
    
    flash("Password changed successfully!", "success")
    return redirect(url_for("user_profile"))

@app.route("/user/add_vehicle", methods=["POST"])
def add_vehicle_route():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    user_id = session["user_id"]
    vehicle_number = request.form["vehicle_number"]
    vehicle_type = request.form["vehicle_type"]
    vehicle_model = request.form.get("vehicle_model", "")
    
    from functions import add_vehicle
    if add_vehicle(user_id, vehicle_number, vehicle_type, vehicle_model):
        flash("Vehicle added successfully!", "success")
    else:
        flash("Failed to add vehicle. Vehicle number might already exist.", "error")
    
    return redirect(url_for("user_profile"))

@app.route("/user/update_vehicle", methods=["POST"])
def update_vehicle_route():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    vehicle_id = request.form["vehicle_id"]
    vehicle_number = request.form["vehicle_number"]
    vehicle_type = request.form["vehicle_type"]
    vehicle_model = request.form.get("vehicle_model", "")
    
    # Verify the vehicle belongs to the current user
    from functions import get_vehicle_by_id, update_vehicle
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or vehicle[1] != session["user_id"]:
        flash("Unauthorized access!", "error")
        return redirect(url_for("user_profile"))
    
    if update_vehicle(vehicle_id, vehicle_number, vehicle_type, vehicle_model):
        flash("Vehicle updated successfully!", "success")
    else:
        flash("Failed to update vehicle. Vehicle number might already exist.", "error")
    
    return redirect(url_for("user_profile"))

@app.route("/user/delete_vehicle", methods=["POST"])
def delete_vehicle_route():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    vehicle_id = request.form["vehicle_id"]
    
    # Verify the vehicle belongs to the current user
    from functions import get_vehicle_by_id, delete_vehicle
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or vehicle[1] != session["user_id"]:
        flash("Unauthorized access!", "error")
        return redirect(url_for("user_profile"))
    
    if delete_vehicle(vehicle_id):
        flash("Vehicle deleted successfully!", "success")
    else:
        flash("Cannot delete vehicle with booking history!", "error")
    
    return redirect(url_for("user_profile"))

@app.route("/user/set_primary_vehicle", methods=["POST"])
def set_primary_vehicle_route():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    user_id = session["user_id"]
    vehicle_id = request.form["vehicle_id"]
    
    # Verify the vehicle belongs to the current user
    from functions import get_vehicle_by_id, set_primary_vehicle
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle or vehicle[1] != user_id:
        flash("Unauthorized access!", "error")
        return redirect(url_for("user_profile"))
    
    if set_primary_vehicle(user_id, vehicle_id):
        flash("Primary vehicle updated successfully!", "success")
    else:
        flash("Failed to update primary vehicle!", "error")
    
    return redirect(url_for("user_profile"))

# -------- Admin Routes --------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        data = request.form
        admin_id = data["admin_id"]
        password = data["password"]
        
        success = login_admin(admin_id, password)
        
        if success:
            session["admin_id"] = admin_id
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "error")
    
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    flash("Admin logged out successfully!", "success")
    return redirect(url_for("index"))

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    # Get statistics
    total_users = get_total_users_count()
    total_parking_lots = get_total_parking_lots_count()
    total_bookings = get_total_bookings_count()
    active_bookings = get_active_bookings_count()
    
    # Get parking lots with occupancy
    parking_lots = get_parking_lots_with_occupancy()
    
    # Get recent users
    recent_users = get_recent_users(10)
    
    # Get recent bookings
    recent_bookings = get_recent_bookings(10)
    
    from functions import get_total_revenue
    total_revenue = get_total_revenue()
    
    return render_template("admin_dashboard.html",
                         total_users=total_users,
                         total_parking_lots=total_parking_lots,
                         total_bookings=total_bookings,
                         active_bookings=active_bookings,
                         parking_lots=parking_lots,
                         recent_users=recent_users,
                         recent_bookings=recent_bookings,
                         total_revenue=total_revenue)

@app.route("/admin/users")
def admin_users():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    users = get_all_users_with_vehicle_count()
    return render_template("admin_users.html", users=users)

@app.route("/admin/parking-lots")
def admin_parking_lots():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    parking_lots = get_all_parking_lots_with_spots()
    return render_template("admin_parking_lots.html", parking_lots=parking_lots)

@app.route("/admin/add-parking-lot", methods=["GET", "POST"])
def admin_add_parking_lot():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    if request.method == "POST":
        data = request.form
        location = data["location"]
        price = float(data["price"])
        area = data["area"]
        pin_code = data["pin_code"]
        spots = int(data["spots"])
        
        add_parking_lot(location, price, area, pin_code, spots)
        flash("Parking lot added successfully!", "success")
        return redirect(url_for("admin_parking_lots"))
    
    return render_template("admin_add_parking_lot.html", 
                         title="Add New Parking Lot",
                         subtitle="Create a new parking lot with spots",
                         back_url=url_for("admin_parking_lots"),
                         back_text="Back to Lots")

@app.route("/admin/edit-parking-lot/<int:lot_id>", methods=["GET", "POST"])
def admin_edit_parking_lot(lot_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    if request.method == "POST":
        data = request.form
        location = data["location"]
        price = float(data["price"])
        area = data["area"]
        pin_code = data["pin_code"]
        spots = int(data["spots"])
        
        update_parking_lot(lot_id, location, price, area, pin_code, spots)
        flash("Parking lot updated successfully! Spot grid has been refreshed.", "success")
        return redirect(url_for("admin_parking_lots"))
    
    parking_lot = get_parking_lot_by_id(lot_id)
    return render_template("admin_edit_parking_lot.html", parking_lot=parking_lot)

@app.route("/admin/delete-parking-lot/<int:lot_id>", methods=["POST"])
def admin_delete_parking_lot(lot_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    delete_parking_lot(lot_id)
    flash("Parking lot deleted successfully!", "success")
    return redirect(url_for("admin_parking_lots"))

@app.route("/admin/search")
def admin_search():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    search_type = request.args.get("type", "users")
    search_category = request.args.get("category", "all")
    search_query = request.args.get("q", "")
    
    results = []
    if search_query:
        if search_type == "users":
            results = search_users_by_category(search_query, search_category)
        elif search_type == "parking_lots":
            results = search_parking_lots_by_category(search_query, search_category)
        elif search_type == "bookings":
            results = search_bookings_by_category(search_query, search_category)
    
    return render_template("admin_search.html", 
                         search_type=search_type, 
                         search_category=search_category,
                         search_query=search_query, 
                         results=results)

@app.route("/admin/summary")
def admin_summary():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    # Get statistics for charts
    revenue_by_lot = get_revenue_by_parking_lot()
    occupancy_by_lot = get_occupancy_by_parking_lot()
    bookings_by_month = get_bookings_by_month()
    
    from functions import get_total_revenue
    total_revenue = get_total_revenue()
    
    # Calculate total revenue
    # total_revenue = sum(revenue[3] for revenue in revenue_by_lot) # This line is now redundant as total_revenue is fetched directly
    
    # Calculate average occupancy
    total_spots = 0
    total_occupied = 0
    for occupancy in occupancy_by_lot:
        total_spots += occupancy[1]
        total_occupied += occupancy[2]
    
    avg_occupancy = (total_occupied / total_spots * 100) if total_spots > 0 else 0
    
    # Get today's bookings
    today_bookings = get_today_bookings_count()
    
    # Get active spots count
    active_spots = get_active_bookings_count()
    
    return render_template("admin_summary.html",
                         revenue_by_lot=revenue_by_lot,
                         occupancy_by_lot=occupancy_by_lot,
                         bookings_by_month=bookings_by_month,
                         total_revenue=total_revenue,
                         avg_occupancy=round(avg_occupancy, 1),
                         today_bookings=today_bookings,
                         active_spots=active_spots)

@app.route("/admin/spot-details/<int:spot_id>")
def admin_spot_details(spot_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    spot_details = get_spot_details_with_booking(spot_id)
    return render_template("admin_spot_details.html", spot_details=spot_details)

@app.route("/admin/delete-spot/<int:spot_id>", methods=["POST"])
def admin_delete_spot(spot_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    success = delete_parking_spot(spot_id)
    if success:
        flash("Parking spot deleted successfully!", "success")
    else:
        flash("Cannot delete occupied parking spot!", "error")
    
    return redirect(url_for("admin_parking_lots"))

@app.route("/admin/add-user", methods=["GET", "POST"])
def admin_add_user():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    if request.method == "POST":
        data = request.form
        name = data["name"]
        email = data["email"]
        phone = data["phone"]
        vehicle = data["vehicle"]
        password = data["password"]
        
        insert_user(name, email, phone, vehicle, password)
        flash("User added successfully!", "success")
        return redirect(url_for("admin_users"))
    
    return render_template("admin_add_user.html")

@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
def admin_delete_user(user_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    # Delete user from database
    conn = sqlite3.connect("parking.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    flash("User deleted successfully!", "success")
    return redirect(url_for("admin_users"))

@app.route("/admin/edit-user/<int:user_id>", methods=["GET", "POST"])
def admin_edit_user(user_id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    
    if request.method == "POST":
        data = request.form
        name = data["name"]
        email = data["email"]
        phone = data["phone"]
        vehicle = data["vehicle"]
        
        # Update user information
        update_user_name_by_id(user_id, name)
        update_user_email_by_id(user_id, email)
        update_user_vehicle_number_by_id(user_id, vehicle)
        
        flash("User updated successfully!", "success")
        return redirect(url_for("admin_users"))
    
    user = get_user_by_id(user_id)
    return render_template("admin_edit_user.html", user=user)

# -------- API Routes --------

@app.route("/api/get_spots/<int:lot_id>")
def get_spots_api(lot_id):
    if "user_id" not in session and "admin_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    from functions import get_spots_by_lot_full
    spots = get_spots_by_lot_full(lot_id)
    
    # Convert to the format expected by JavaScript
    formatted_spots = []
    for spot in spots:
        formatted_spots.append({
            "id": spot[0],
            "spot_number": spot[1],
            "level": spot[2],
            "status": spot[3]
        })
    
    return jsonify({"spots": formatted_spots})

@app.route("/user/summary")
def user_summary():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    user_id = session["user_id"]
    from functions import get_user_bookings_by_date, get_user_bookings_by_slot, get_user_bookings_by_vehicle
    data = get_user_bookings_by_date(user_id)
    labels = [row[0] for row in data]
    counts = [row[1] for row in data]
    slot_data = get_user_bookings_by_slot(user_id)
    slot_labels = [row[0] for row in slot_data]
    slot_counts = [row[1] for row in slot_data]
    vehicle_data = get_user_bookings_by_vehicle(user_id)
    vehicle_labels = [f"{row[0]} ({row[1]})" for row in vehicle_data]
    vehicle_counts = [row[2] for row in vehicle_data]
    
    return render_template("user_summary.html", 
                         labels=labels, 
                         data=counts, 
                         slot_labels=slot_labels, 
                         slot_counts=slot_counts,
                         vehicle_labels=vehicle_labels,
                         vehicle_data=vehicle_counts)

@app.route("/user/search")
def user_search():
    if "user_id" not in session:
        return redirect(url_for("user_login"))
    
    user_id = session["user_id"]
    search_category = request.args.get("category", "all")
    search_query = request.args.get("q", "")
    price_filter = request.args.get("price_filter", "")
    
    from functions import search_parking_lots_for_users, get_total_parking_lots_count, get_user_vehicles
    
    results = []
    total_lots = get_total_parking_lots_count()
    vehicles = get_user_vehicles(user_id)
    
    # For "Previously Booked" category, don't require a search query
    if search_query or price_filter or search_category == "previously_booked":
        results = search_parking_lots_for_users(search_query, search_category, price_filter, user_id)
    
    return render_template("user_search.html", 
                         search_category=search_category,
                         search_query=search_query, 
                         price_filter=price_filter,
                         results=results,
                         total_lots=total_lots,
                         vehicles=vehicles)

@app.route("/api/admin/lot_spots/<int:lot_id>")
def api_admin_lot_spots(lot_id):
    if "admin_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    from functions import get_spots_by_lot_full
    spots = get_spots_by_lot_full(lot_id)
    
    # Convert to the format expected by admin interface
    formatted_spots = []
    for spot in spots:
        formatted_spots.append({
            "id": spot[0],
            "spot_number": spot[1],
            "level": spot[2],
            "status": spot[3]
        })
    
    return jsonify({"spots": formatted_spots})

@app.route("/api/admin/spot_details/<int:spot_id>")
def api_admin_spot_details(spot_id):
    if "admin_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    from functions import get_admin_spot_details
    details = get_admin_spot_details(spot_id)
    return jsonify({"details": details})

@app.route("/api/booking_details/<int:booking_id>")
def api_booking_details(booking_id):
    if "user_id" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    from functions import get_booking_details
    details = get_booking_details(booking_id)
    if details:
        return jsonify({
            "id": details[0],
            "spot_number": details[2],
            "status": details[3],
            "location": details[4],
            "price": details[5],
            "created_at": details[7],
            "completed_at": details[8],
            "vehicle_number": details[9],
            "vehicle_type": details[10]
        })
    else:
        return jsonify({"error": "Booking not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
