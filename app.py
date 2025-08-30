from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
if not os.path.exists(os.path.join(basedir, 'database')):
    os.makedirs(os.path.join(basedir, 'database'))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'parking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    vehicle_brand = db.Column(db.String(100), nullable=False)
    vehicle_no = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    spots = db.relationship('ParkingSpot', backref='parking_lot', lazy=True, cascade='all, delete-orphan')

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    spot_number = db.Column(db.String(10), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    bookings = db.relationship('Booking', backref='spot', lazy=True)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    vehicle_no = db.Column(db.String(20), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False)
    exit_time = db.Column(db.DateTime, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Helper decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))

        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.is_admin:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Try username first, then email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin

            if user.is_admin:
                flash('Welcome back, Admin!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash(f'Welcome back, {user.first_name}!', 'success')
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password!', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        address = request.form['address']
        pincode = request.form['pincode']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic validation
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html', form_data=request.form)

        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html', form_data=request.form)

        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html', form_data=request.form)

        # Create new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            address=address,
            pincode=pincode,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# User Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    vehicles = Vehicle.query.filter_by(user_id=user.id).all()
    bookings = db.session.query(Booking, ParkingLot, ParkingSpot, Vehicle).\
        join(ParkingSpot, Booking.spot_id == ParkingSpot.id).\
        join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id).\
        join(Vehicle, Booking.vehicle_no == Vehicle.vehicle_no).\
        filter(Booking.user_id == user.id).\
        order_by(Booking.created_at.desc()).limit(5).all()

    stats = {
        'total_vehicles': len(vehicles),
        'total_bookings': Booking.query.filter_by(user_id=user.id).count(),
        'active_bookings': Booking.query.filter_by(user_id=user.id, status='active').count()
    }

    return render_template('dashboard.html', user=user, stats=stats, recent_bookings=bookings)

# Vehicle Management
@app.route('/vehicles', methods=['GET', 'POST'])
@login_required
def vehicle_register():
    if request.method == 'POST':
        # Check if vehicle already exists
        if Vehicle.query.filter_by(vehicle_no=request.form['vehicle_no']).first():
            flash('Vehicle number already registered!', 'error')
            return render_template('vehicle_register.html', 
                                 vehicles=Vehicle.query.filter_by(user_id=session['user_id']).all())

        vehicle = Vehicle(
            user_id=session['user_id'],
            owner_name=request.form['owner_name'],
            mobile=request.form['mobile'],
            vehicle_type=request.form['vehicle_type'],
            vehicle_brand=request.form['vehicle_brand'],
            vehicle_no=request.form['vehicle_no'].upper()
        )

        db.session.add(vehicle)
        db.session.commit()
        flash('Vehicle registered successfully!', 'success')
        return redirect(url_for('vehicle_register'))

    vehicles = Vehicle.query.filter_by(user_id=session['user_id']).all()
    return render_template('vehicle_register.html', vehicles=vehicles)

# Parking Lot Search & Booking
@app.route('/parking_lots')
@login_required
def parking_lots():
    search_pincode = request.args.get('pincode', '')
    search_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

    query = ParkingLot.query
    if search_pincode:
        query = query.filter(ParkingLot.pincode.like(f'%{search_pincode}%'))

    lots = query.all()

    # Calculate availability for each lot
    lots_with_availability = []
    for lot in lots:
        total_spots = len(lot.spots)
        # For simplicity, we'll just count available spots (in real app, consider date/time)
        available_spots = len([spot for spot in lot.spots if spot.is_available])
        lots_with_availability.append({
            'lot': lot,
            'total_spots': total_spots,
            'available_spots': available_spots,
            'utilization': ((total_spots - available_spots) / total_spots * 100) if total_spots > 0 else 0
        })

    # Get user vehicles for booking
    vehicles = Vehicle.query.filter_by(user_id=session['user_id']).all()

    return render_template('parking_lots.html', 
                         lots_data=lots_with_availability, 
                         vehicles=vehicles,
                         search_pincode=search_pincode,
                         search_date=search_date)

@app.route('/book_parking', methods=['POST'])
@login_required
def book_parking():
    lot_id = request.form['lot_id']
    vehicle_id = request.form['vehicle_id']
    entry_time = datetime.strptime(request.form['entry_time'], '%Y-%m-%dT%H:%M')
    exit_time = datetime.strptime(request.form['exit_time'], '%Y-%m-%dT%H:%M')

    # Find available spot in the lot
    available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, is_available=True).first()
    if not available_spot:
        flash('No available spots in this parking lot!', 'error')
        return redirect(url_for('parking_lots'))

    # Get vehicle and lot details
    vehicle = Vehicle.query.get(vehicle_id)
    lot = ParkingLot.query.get(lot_id)

    # Calculate cost
    duration_hours = (exit_time - entry_time).total_seconds() / 3600
    total_cost = duration_hours * lot.price_per_hour

    # Create booking
    booking = Booking(
        user_id=session['user_id'],
        spot_id=available_spot.id,
        vehicle_no=vehicle.vehicle_no,
        entry_time=entry_time,
        exit_time=exit_time,
        total_cost=total_cost
    )

    # Mark spot as unavailable
    available_spot.is_available = False

    db.session.add(booking)
    db.session.commit()

    flash('Parking spot booked successfully!', 'success')
    return render_template('confirm_booking.html', 
                         booking=booking, 
                         parking_lot=lot, 
                         spot=available_spot, 
                         vehicle=vehicle)

@app.route('/my_bookings')
@login_required
def view_reservations():
    bookings = db.session.query(Booking, ParkingLot, ParkingSpot, Vehicle).\
        join(ParkingSpot, Booking.spot_id == ParkingSpot.id).\
        join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id).\
        join(Vehicle, Booking.vehicle_no == Vehicle.vehicle_no).\
        filter(Booking.user_id == session['user_id']).\
        order_by(Booking.created_at.desc()).all()

    return render_template('view_reservations.html', bookings=bookings)

@app.route('/release_parking/<int:booking_id>')
@login_required
def release_parking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Verify booking belongs to current user
    if booking.user_id != session['user_id']:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('view_reservations'))

    # Release the spot
    spot = ParkingSpot.query.get(booking.spot_id)
    spot.is_available = True
    booking.status = 'completed'

    db.session.commit()
    flash('Parking spot released successfully!', 'success')
    return redirect(url_for('view_reservations'))

# Admin Routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Get statistics
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    total_users = User.query.filter_by(is_admin=False).count()
    total_bookings = Booking.query.count()
    active_bookings = Booking.query.filter_by(status='active').count()

    # Calculate total revenue
    total_revenue = db.session.query(db.func.sum(Booking.total_cost)).scalar() or 0

    # Get recent bookings
    recent_bookings = db.session.query(Booking, User, ParkingLot, ParkingSpot).\
        join(User, Booking.user_id == User.id).\
        join(ParkingSpot, Booking.spot_id == ParkingSpot.id).\
        join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id).\
        order_by(Booking.created_at.desc()).limit(5).all()

    stats = {
        'total_lots': total_lots,
        'total_spots': total_spots,
        'total_users': total_users,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_revenue': total_revenue
    }

    return render_template('admin/dashboard.html', stats=stats, recent_bookings=recent_bookings)

@app.route('/admin/parking_lots')
@admin_required
def admin_parking_lots():
    lots = ParkingLot.query.all()
    lots_data = []

    for lot in lots:
        total_spots = len(lot.spots)
        available_spots = len([spot for spot in lot.spots if spot.is_available])
        lots_data.append({
            'lot': lot,
            'total_spots': total_spots,
            'available_spots': available_spots,
            'utilization': ((total_spots - available_spots) / total_spots * 100) if total_spots > 0 else 0
        })

    return render_template('admin/parking_lots.html', lots_data=lots_data)

@app.route('/admin/add_lot', methods=['GET', 'POST'])
@admin_required
def add_lot():
    if request.method == 'POST':
        lot = ParkingLot(
            name=request.form['name'],
            address=request.form['address'],
            pincode=request.form['pincode'],
            price_per_hour=float(request.form['price_per_hour']),
            capacity=int(request.form['capacity'])
        )

        db.session.add(lot)
        db.session.flush()  # Get the lot ID

        # Create parking spots
        for i in range(1, lot.capacity + 1):
            spot = ParkingSpot(
                lot_id=lot.id,
                spot_number=f'P{i:03d}'
            )
            db.session.add(spot)

        db.session.commit()
        flash(f'Parking lot "{lot.name}" created with {lot.capacity} spots!', 'success')
        return redirect(url_for('admin_parking_lots'))

    return render_template('admin/add_lot.html')

@app.route('/admin/edit_lot/<int:lot_id>', methods=['GET', 'POST'])
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == 'POST':
        old_capacity = lot.capacity

        lot.name = request.form['name']
        lot.address = request.form['address']
        lot.pincode = request.form['pincode']
        lot.price_per_hour = float(request.form['price_per_hour'])
        lot.capacity = int(request.form['capacity'])

        # Handle capacity changes
        if lot.capacity != old_capacity:
            if lot.capacity > old_capacity:
                # Add more spots
                current_spots = len(lot.spots)
                for i in range(current_spots + 1, lot.capacity + 1):
                    spot = ParkingSpot(
                        lot_id=lot.id,
                        spot_number=f'P{i:03d}'
                    )
                    db.session.add(spot)
            else:
                # Remove excess spots (only if they're available)
                spots_to_remove = ParkingSpot.query.filter_by(
                    lot_id=lot.id, is_available=True
                ).offset(lot.capacity).all()

                for spot in spots_to_remove:
                    db.session.delete(spot)

        db.session.commit()
        flash(f'Parking lot "{lot.name}" updated successfully!', 'success')
        return redirect(url_for('admin_parking_lots'))

    return render_template('admin/edit_lot.html', lot=lot)

@app.route('/admin/delete_lot/<int:lot_id>')
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    # Check if there are active bookings
    active_bookings = db.session.query(Booking).\
        join(ParkingSpot, Booking.spot_id == ParkingSpot.id).\
        filter(ParkingSpot.lot_id == lot_id, Booking.status == 'active').count()

    if active_bookings > 0:
        flash('Cannot delete parking lot with active bookings!', 'error')
        return redirect(url_for('admin_parking_lots'))

    db.session.delete(lot)
    db.session.commit()
    flash(f'Parking lot "{lot.name}" deleted successfully!', 'success')
    return redirect(url_for('admin_parking_lots'))

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/bookings')
@admin_required
def admin_bookings():
    bookings = db.session.query(Booking, User, ParkingLot, ParkingSpot).\
        join(User, Booking.user_id == User.id).\
        join(ParkingSpot, Booking.spot_id == ParkingSpot.id).\
        join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id).\
        order_by(Booking.created_at.desc()).all()

    return render_template('admin/bookings.html', bookings=bookings)

# Initialize database and create admin user
def create_admin_user():
    """Create default admin user if it doesn't exist"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            first_name='System',
            last_name='Administrator',
            username='admin',
            email='admin@parking.com',
            address='System Administrator',
            pincode='000000',
            password=generate_password_hash('Admin@123'),  # Fixed password with caps and special char
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("Username: admin")
        print("Password: Admin@123")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()

    print("\n" + "="*50)
    print("🚗 Vehicle Parking Management System")
    print("="*50)
    print("Admin Login:")
    print("Username: admin")
    print("Password: Admin@123")  # Fixed password
    print("="*50)

    app.run(debug=True, host='0.0.0.0', port=5000)
