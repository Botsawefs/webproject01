from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

# ── App setup ──────────────────────────────────────────────────────────────
app = Flask(__name__)
# The secret key is required to encrypt "sessions" (the login wristband)
app.secret_key = 'gmt_sorabora_secret_2025'

# Absolute path so DB is found regardless of where Flask is launched from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'mydata.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Auth Helper ────────────────────────────────────────────────────────────
def is_logged_in():
    return session.get('logged_in') == True


# ── Public pages (No Login Required) ───────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/staff')
def staff():
    return render_template('staff.html')


# ── Gatekeeper: Simple Login ───────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw   = request.form.get('password')
        
        # Simple hardcoded credentials as requested
        if user == 'staff' and pw == 'sorabora2025':
            session['logged_in'] = True
            flash('Access Authorized. Welcome back.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Access Denied.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ── Public booking ─────────────────────────────────────────────────────────
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        first     = request.form.get('firstName', '').strip()
        last      = request.form.get('lastName', '').strip()
        name      = f'{first} {last}'.strip()
        room_type = request.form.get('room', 'lake')
        check_in  = request.form.get('checkIn', '')
        
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO bookings (name, room_type, check_in) VALUES (?, ?, ?)',
            (name, room_type, check_in)
        )
        conn.commit()
        conn.close()
        return render_template('booking.html', submitted=True)
    return render_template('booking.html', submitted=False)


# ── Staff: Room Management (PROTECTED) ─────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    conn     = get_db_connection()
    rooms    = conn.execute('SELECT * FROM room_status ORDER BY room_number').fetchall()
    bookings = conn.execute('SELECT * FROM bookings ORDER BY id DESC').fetchall()
    conn.close()
    
    total     = len(rooms)
    occupied  = sum(1 for r in rooms if r['status'] == 'Occupied')
    available = total - occupied
    
    return render_template(
        'room_management.html',
        rooms=rooms, bookings=bookings,
        total=total, occupied=occupied, available=available
    )


# ── Staff: Premises Management (PROTECTED) ──────────────────────────────────
@app.route('/premises_management')
def premises():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    # You can eventually fetch maintenance logs or stock from the DB here
    return render_template('premises_management.html')


# ── Update / Add / Delete Actions (All PROTECTED) ──────────────────────────
@app.route('/update_room', methods=['POST'])
def update_room():
    if not is_logged_in(): return redirect(url_for('login'))
    
    room_num  = request.form.get('room_number')
    guest     = request.form.get('guest_name', '').strip()
    status    = request.form.get('status')
    check_out = request.form.get('check_out_date', '')
    
    if not room_num:
        flash('Room number is required.', 'error')
        return redirect(url_for('dashboard'))
        
    if status == 'Available':
        guest = ''
        check_out = ''
        
    conn = get_db_connection()
    conn.execute(
        'UPDATE room_status SET status=?, customer_name=?, check_out_date=? WHERE room_number=?',
        (status, guest, check_out or None, room_num)
    )
    conn.commit()
    conn.close()
    flash(f'Room {room_num} updated successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/add_room', methods=['POST'])
def add_room():
    if not is_logged_in(): return redirect(url_for('login'))
    
    room_num  = request.form.get('room_number')
    room_type = request.form.get('room_type')
    
    if not room_num:
        flash('Room number is required.', 'error')
        return redirect(url_for('dashboard'))
        
    conn = get_db_connection()
    if conn.execute('SELECT 1 FROM room_status WHERE room_number=?', (room_num,)).fetchone():
        conn.close()
        flash(f'Room {room_num} already exists.', 'error')
        return redirect(url_for('dashboard'))
        
    conn.execute(
        'INSERT INTO room_status (room_number, room_type, status) VALUES (?, ?, ?)',
        (room_num, room_type, 'Available')
    )
    conn.commit()
    conn.close()
    flash(f'Room {room_num} ({room_type}) added.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_room', methods=['POST'])
def delete_room():
    if not is_logged_in(): return redirect(url_for('login'))
    
    room_num = request.form.get('room_number')
    conn = get_db_connection()
    conn.execute('DELETE FROM room_status WHERE room_number=?', (room_num,))
    conn.commit()
    conn.close()
    flash(f'Room {room_num} removed.', 'success')
    return redirect(url_for('dashboard'))


# At the very bottom of app.py
if __name__ == "__main__":
    app.run(debug=True)