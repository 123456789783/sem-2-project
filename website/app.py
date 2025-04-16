import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT )')
    conn.commit()
    conn.close()
    
def get_db_connection():
    return sqlite3.connect(DB_FILE)

def authentecate_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()

init_db()

@app.route("/")
def index():
    return render_template("home.html")

@app.route('/mekanism')
def mekanism():
    return render_template('mekanism.html')

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

# Main function that starts the app
if __name__ == "__main__":
    app.run(debug=True, port=3000)