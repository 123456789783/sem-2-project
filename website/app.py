# Import required libraries
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from datetime import datetime

# Create Flask app
app = Flask(__name__)
app.secret_key = 'asdgfnjlskdfjkldfjnb'  # Secret key for session

# Set up database and upload folder
DB_FILE = "database.db"
upload_folder = os.path.join('static', 'Image')
app.config['UPLOAD'] = upload_folder

# Initialize the database and create tables if they don't exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, profile IMG )')
    cursor.execute('CREATE TABLE IF NOT EXISTS comments (commentId INTEGER PRIMARY KEY AUTOINCREMENT, parentID INTEGER, comment TEXT, date TEXT, page TEXT, username TEXT)')
    conn.commit()
    conn.close()

# Open a connection to the database
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Check if username and password are correct
def authentecate_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? and password = ?', (username, password))
    user = c.fetchone()
    return user is not None

# Build the comment tree for a specific page used to simplify code
def build_comment_tree(page_name):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT commentId, parentID, comment, date, username FROM comments WHERE page = ? ORDER BY date DESC', (page_name,))
    comments = c.fetchall()
    conn.close()
    
    comment_tree = {}

    # Grab all parent comments
    for comment in comments:
        comment = dict(comment)
        comment_id = comment['commentId']
        parent_id = comment['parentID']
        if parent_id is None:
            comment_tree[comment_id] = {'comment': comment, 'reply': []}
    
    # Add replies to the parent comments
    for comment in comments:
        comment = dict(comment)
        comment_id = comment['commentId']
        parent_id = comment['parentID']
        if parent_id is not None:
            if parent_id in comment_tree:
                comment_tree[comment_id] = {'comment': comment, 'reply': []}
                comment_tree[parent_id]['reply'].append(comment_tree[comment_id])
    
    return comment_tree

# Initialize the database tables
init_db()

# Home page
@app.route("/")
def index():
    return render_template("home.html")

# Page for mekanism
@app.route('/mekanism')
def mekanism():
    comment_tree = build_comment_tree('mekanism')
    username = session.get('user')
    return render_template('mekanism.html', comment_tree=comment_tree, logged_in_user=username)

# Page for industrial_foregoing
@app.route('/industrial_foregoing')
def industrial_foregoing():
    comment_tree = build_comment_tree('industrial_foregoing')
    username = session.get('user')
    return render_template('industrial_foregoing.html', comment_tree=comment_tree, logged_in_user=username)

# Page for mystical_agriculture
@app.route('/mystical_agriculture')
def mystical_agriculture():
    comment_tree = build_comment_tree('mystical_agriculture')
    username = session.get('user')
    return render_template('mystical_agriculture.html', comment_tree=comment_tree, logged_in_user=username)

# Info page
@app.route('/info')
def info():
    return render_template('info.html')

# Register a new user
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
            flash("Username already exists.", 'overlay')
            return render_template('register.html')
        finally:
            conn.close()
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':  
        username = request.form['username']
        password = request.form['password']
        if authentecate_user(username, password):
            session['user'] = username
            return render_template('home.html')
        else:
            flash("Incorrect username or password.", 'overlay')
    return render_template('login.html')

# Logout route
@app.route('/Logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# Post a comment to database with date and time
@app.route('/comment', methods=['GET', 'POST'])
def post_comment():
    if 'user' not in session:
        flash('You must be signed in to post a comment.', 'overlay')
        return redirect(request.referrer)

    page = request.form['page']
    username = session.get('user')
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    parent_id = request.form.get('parentID')
    comment = request.form['comment']
    
    if not comment:
        flash('Type something', 'overlay')
        return redirect(request.referrer)
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO comments (comment, date, page, parentID, username) VALUES (?, ?, ?, ?, ?)', (comment, date, page, parent_id, username))
    conn.commit()
    conn.close()
    return redirect(url_for(page))

# Upload image test page
@app.route('/uploadtest', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['img']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD'], filename))
        img = os.path.join(app.config['UPLOAD'], filename)
        return render_template('uploadtest.html', img=img)
    return render_template('uploadtest.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=3000)
