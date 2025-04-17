from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'


# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS farmers (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 farmer_id TEXT UNIQUE,
                 name TEXT,
                 email TEXT,
                 password TEXT
                 )''')
    conn.commit()
    conn.close()

init_db()


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/sinup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        farmer_id = str(uuid.uuid4())[:8]  # Generate unique 8-char ID

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO farmers (farmer_id, name, email, password) VALUES (?, ?, ?, ?)",
                      (farmer_id, name, email, password))
            conn.commit()
            flash(f"Signup successful! Your Farmer ID is: {farmer_id}", "success")
        except sqlite3.IntegrityError:
            flash("Email already exists!", "danger")
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('sinup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT email FROM farmers WHERE farmer_id = ? AND password = ?", (farmer_id, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['farmer_id'] = farmer_id
            session['email'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "danger")
    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'farmer_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', farmer_id=session['farmer_id'], email=session['email'])


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        farmer_id = request.form['farmer_id']
        new_password = request.form['new_password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM farmers WHERE farmer_id = ?", (farmer_id,))
        user = c.fetchone()

        if user:
            c.execute("UPDATE farmers SET password = ? WHERE farmer_id = ?", (new_password, farmer_id))
            conn.commit()
            flash("Password updated successfully!", "success")
            conn.close()
            return redirect(url_for('login'))
        else:
            flash("Farmer ID not found!", "danger")
            conn.close()
    return render_template('password_reset.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
