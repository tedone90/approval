
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import shutil
import os
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flight_date TEXT,
            client TEXT,
            price REAL,
            ref_avinode TEXT,
            ref_fl3xx TEXT,
            status TEXT,
            notes TEXT,
            handler TEXT
        )
    ''')
    conn.commit()
    conn.close()
    os.makedirs('backup', exist_ok=True)

@app.route('/')
def home():
    return redirect(url_for('index'))

@app.route('/index', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    if request.method == 'POST':
        search = request.form['search']
        query = "SELECT * FROM flights WHERE client LIKE ? OR ref_avinode LIKE ? OR ref_fl3xx LIKE ? OR status LIKE ? OR notes LIKE ? OR handler LIKE ? ORDER BY date(flight_date) ASC"
        flights = conn.execute(query, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%')).fetchall()
    else:
        flights = conn.execute('SELECT * FROM flights ORDER BY date(flight_date) ASC').fetchall()
    conn.close()

    today = datetime.now().date()
    upcoming_flights = []
    for flight in flights:
        try:
            flight_date = datetime.strptime(flight['flight_date'], "%Y-%m-%d").date()
            if today <= flight_date <= today + timedelta(days=5):
                upcoming_flights.append(flight['id'])
        except:
            continue

    return render_template('index.html', flights=flights, upcoming_flights=upcoming_flights)

@app.route('/add', methods=['GET', 'POST'])
def add_flight():
    if request.method == 'POST':
        flight_date = request.form['flight_date']
        client = request.form['client']
        price = request.form['price']
        ref_avinode = request.form['ref_avinode']
        ref_fl3xx = request.form['ref_fl3xx']
        status = request.form['status']
        notes = request.form['notes']
        handler = request.form['handler']

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO flights (flight_date, client, price, ref_avinode, ref_fl3xx, status, notes, handler)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (flight_date, client, price, ref_avinode, ref_fl3xx, status, notes, handler))
        conn.commit()
        conn.close()

        backup_database()

        return redirect(url_for('index'))
    return render_template('add_flight.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_flight(id):
    conn = get_db_connection()
    flight = conn.execute('SELECT * FROM flights WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        flight_date = request.form['flight_date']
        client = request.form['client']
        price = request.form['price']
        ref_avinode = request.form['ref_avinode']
        ref_fl3xx = request.form['ref_fl3xx']
        status = request.form['status']
        notes = request.form['notes']
        handler = request.form['handler']

        conn.execute('''
            UPDATE flights
            SET flight_date = ?, client = ?, price = ?, ref_avinode = ?, ref_fl3xx = ?, status = ?, notes = ?, handler = ?
            WHERE id = ?
        ''', (flight_date, client, price, ref_avinode, ref_fl3xx, status, notes, handler, id))
        conn.commit()
        conn.close()

        backup_database()

        return redirect(url_for('index'))
    conn.close()
    return render_template('edit_flight.html', flight=flight)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_flight(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM flights WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    backup_database()

    return redirect(url_for('index'))

def backup_database():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if os.path.exists('database.db'):
        shutil.copy('database.db', f'backup/database_{timestamp}.db')

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
