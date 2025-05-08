import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'asdgfnjlskdfjkldfjnb'
DB_FILE = "database.db"
upload_folder = os.path.join('static', 'Image')
app.config['UPLOAD'] = upload_folder

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT )')
    cursor.execute('CREATE TABLE IF NOT EXISTS comments (commentId INTEGER PRIMARY KEY AUTOINCREMENT, parentID INTEGER, comment TEXT, date TEXT, page TEXT)')
    conn.commit()
    conn.close()
    
def get_db_connection():
    return sqlite3.connect(DB_FILE)

def authentecate_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE username = ? and password = ?', (username,password))
    user = c.fetchone()
    return user is not None

init_db()

@app.route("/")
def index():
    return render_template("home.html")

@app.route('/mekanism')
def mekanism():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT comment, date FROM comments WHERE page = "mekanism" ORDER BY date DESC')
    comments = c.fetchall()
    conn.close()
    username = session.get('user')
    return render_template('mekanism.html', comments = comments, logged_in_user = username)

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return render_template('login.html')
        except sqlite3.IntegrityError:
            return f"Username already exists."
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if authentecate_user(username, password):
        session['user'] = username
        return render_template('home.html')
    else:
        return f"incorrect username or password"
    
    return render_template('login.html')

@app.route('/Logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
    

@app.route('/comment', methods=['GET', 'POST'])
def post_comment():
    
    if 'user' not in session:
        flash('You must be signed in to post a comment.', 'overlay')
        return redirect(request.referrer)

    page = request.form['page']
    username = session.get('user')
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    comment = request.form['comment']
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO comments (comment, date, page) VALUES (?, ?, ?)', (comment, date, page))
    conn.commit()
    conn.close()
    return redirect(url_for(page))

@app.route('/upload' , methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['img']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD'], filename))
        img = os.path.join(app.config['UPLOAD'], filename)
        return render_template('uploadtest.html', img=img)
    return render_template('uploadtest.html')
 

# Main function that starts the app
if __name__ == "__main__":
    app.run(debug=True, port=3000)