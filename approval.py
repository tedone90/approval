from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from datetime import datetime, timedelta

app = Flask(__name__)

DB_HOST = 'dpg-d07oda49c44c73a6d6q0-a.frankfurt-postgres.render.com'
DB_PORT = '5432'
DB_NAME = 'approval_db_u0ke'
DB_USER = 'approval_db_u0ke_user'
DB_PASSWORD = 'FtY9eYchf9Qpwmjg8R3tv7VTD5TUhp13'

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id SERIAL PRIMARY KEY,
            flight_date DATE,
            client TEXT,
            price FLOAT,
            ref_avinode TEXT,
            ref_fl3xx TEXT,
            status TEXT,
            notes TEXT,
            handler TEXT
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def home():
    return redirect(url_for('index'))

@app.route('/index', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    if request.method == 'POST':
        search = request.form['search']
        cur.execute("""
            SELECT * FROM flights
            WHERE client ILIKE %s OR ref_avinode ILIKE %s OR ref_fl3xx ILIKE %s OR status ILIKE %s OR notes ILIKE %s OR handler ILIKE %s
            ORDER BY flight_date ASC
        """, (f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'))
    else:
        cur.execute('SELECT * FROM flights ORDER BY flight_date ASC')
    flights = cur.fetchall()
    conn.close()

    today = datetime.now().date()
    upcoming_flights = []
    flight_data = []
    for flight in flights:
        flight_obj = {
            'id': flight[0],
            'flight_date': flight[1],
            'client': flight[2],
            'price': flight[3],
            'ref_avinode': flight[4],
            'ref_fl3xx': flight[5],
            'status': flight[6],
            'notes': flight[7],
            'handler': flight[8]
        }
        flight_data.append(flight_obj)
        try:
            if today <= flight[1] <= today + timedelta(days=5):
                upcoming_flights.append(flight[0])
        except:
            continue

    return render_template('index.html', flights=flight_data, upcoming_flights=upcoming_flights)

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
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO flights (flight_date, client, price, ref_avinode, ref_fl3xx, status, notes, handler)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (flight_date, client, price, ref_avinode, ref_fl3xx, status, notes, handler))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('index'))
    return render_template('add_flight.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_flight(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM flights WHERE id = %s', (id,))
    flight = cur.fetchone()

    if request.method == 'POST':
        flight_date = request.form['flight_date']
        client = request.form['client']
        price = request.form['price']
        ref_avinode = request.form['ref_avinode']
        ref_fl3xx = request.form['ref_fl3xx']
        status = request.form['status']
        notes = request.form['notes']
        handler = request.form['handler']

        cur.execute('''
            UPDATE flights
            SET flight_date = %s, client = %s, price = %s, ref_avinode = %s, ref_fl3xx = %s, status = %s, notes = %s, handler = %s
            WHERE id = %s
        ''', (flight_date, client, price, ref_avinode, ref_fl3xx, status, notes, handler, id))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('index'))

    conn.close()
    flight_obj = {
        'id': flight[0],
        'flight_date': flight[1],
        'client': flight[2],
        'price': flight[3],
        'ref_avinode': flight[4],
        'ref_fl3xx': flight[5],
        'status': flight[6],
        'notes': flight[7],
        'handler': flight[8]
    }
    return render_template('edit_flight.html', flight=flight_obj)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_flight(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM flights WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
