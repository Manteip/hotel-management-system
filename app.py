
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Guest (
            guestID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contactNo TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL,
            dob TEXT NOT NULL,
            nationality TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Room (
            roomID INTEGER PRIMARY KEY AUTOINCREMENT,
            roomNum INTEGER NOT NULL,
            type TEXT NOT NULL,
            pricePerNight REAL NOT NULL,
            status TEXT NOT NULL,
            floor INTEGER NOT NULL,
            view TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reservation (
            reservationID INTEGER PRIMARY KEY AUTOINCREMENT,
            guestID INTEGER,
            checkInDate TEXT,
            checkOutDate TEXT,
            numberOfGuests INTEGER,
            specialRequests TEXT,
            FOREIGN KEY (guestID) REFERENCES Guest(guestID)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ReservationRoom (
            reservationID INTEGER,
            roomID INTEGER,
            PRIMARY KEY (reservationID, roomID),
            FOREIGN KEY (reservationID) REFERENCES Reservation(reservationID),
            FOREIGN KEY (roomID) REFERENCES Room(roomID)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Guest')
    guests = cursor.fetchall()
    conn.close()
    return render_template('index.html', guests=guests)

@app.route('/add_guest', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':
        name = request.form['name']
        contactNo = request.form['contactNo']
        email = request.form['email']
        address = request.form['address']
        dob = request.form['dob']
        nationality = request.form['nationality']
        
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Guest (name, contactNo, email, address, dob, nationality)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, contactNo, email, address, dob, nationality))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_guest.html')

@app.route('/guest_reservations', methods=['GET'])
def guest_reservations():
    guest_id = request.args.get('guest_id')
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.roomNum, r.type, r.pricePerNight, r.status 
        FROM Room r
        JOIN ReservationRoom rr ON r.roomID = rr.roomID
        JOIN Reservation res ON rr.reservationID = res.reservationID
        WHERE res.guestID = ?;
    ''', (guest_id,))
    reservations = cursor.fetchall()
    conn.close()
    return render_template('guest_reservations.html', reservations=reservations)

@app.route('/reservations_in_date_range', methods=['GET', 'POST'])
def reservations_in_date_range():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT guest.name, res.checkInDate, res.checkOutDate, res.numberOfGuests
            FROM Reservation res
            JOIN Guest guest ON res.guestID = guest.guestID
            WHERE res.checkInDate BETWEEN ? AND ?;
        ''', (start_date, end_date))
        reservations = cursor.fetchall()
        conn.close()
        return render_template('reservations_in_date_range.html', reservations=reservations)
    return render_template('reservations_in_date_range_form.html')

@app.route('/total_income', methods=['GET', 'POST'])
def total_income():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(r.pricePerNight) * (julianday(res.checkOutDate) - julianday(res.checkInDate)) AS totalIncome
            FROM Reservation res
            JOIN ReservationRoom rr ON res.reservationID = rr.reservationID
            JOIN Room r ON rr.roomID = r.roomID
            WHERE res.checkInDate BETWEEN ? AND ?;
        ''', (start_date, end_date))
        total_income = cursor.fetchone()
        conn.close()
        return render_template('total_income.html', total_income=total_income)
    return render_template('total_income_form.html')

@app.route('/available_rooms', methods=['GET', 'POST'])
def available_rooms():
    if request.method == 'POST':
        room_type = request.form['room_type']
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT roomNum, type, pricePerNight, status 
            FROM Room 
            WHERE status = 'Available' AND type = ?;
        ''', (room_type,))
        available_rooms = cursor.fetchall()
        conn.close()
        return render_template('available_rooms.html', available_rooms=available_rooms)
    return render_template('available_rooms_form.html')

@app.route('/guest_details', methods=['GET'])
def guest_details():
    guest_id = request.args.get('guest_id')
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT guest.name, res.checkInDate, res.checkOutDate, res.specialRequests, r.roomNum
        FROM Reservation res
        JOIN Guest guest ON res.guestID = guest.guestID
        JOIN ReservationRoom rr ON res.reservationID = rr.reservationID
        JOIN Room r ON rr.roomID = r.roomID
        WHERE guest.guestID = ?;
    ''', (guest_id,))
    guest_info = cursor.fetchall()
    conn.close()
    return render_template('guest_details.html', guest_info=guest_info)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
