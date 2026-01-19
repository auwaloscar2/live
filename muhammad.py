from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secretkey123'
UPLOAD_FOLDER = 'uploads'
BOOK_FOLDER = 'books'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BOOK_FOLDER, exist_ok=True)

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# Database setup
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, user TEXT, book TEXT, proof TEXT, approved INTEGER)')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO users VALUES (NULL,?,?)',(u,p))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username=? AND password=?',(u,p))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = u
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/pay', methods=['POST'])
def pay():
    file = request.files['proof']
    filename = secure_filename(file.filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO payments VALUES (NULL,?,?,?,0)',(session['user'],'Art of War',filename))
    conn.commit()
    conn.close()
    return 'Payment submitted. Wait for admin approval.'

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM payments')
    data = c.fetchall()
    conn.close()
    return render_template('admin.html', data=data)

@app.route('/approve/<int:id>')
def approve(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE payments SET approved=1 WHERE id=?',(id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/download')
def download():
    return send_from_directory(BOOK_FOLDER, 'art_of_war.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
