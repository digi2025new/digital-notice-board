from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
import os
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

DATABASE_URL = os.getenv("DATABASE_URL")

socketio = SocketIO(app)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'txt'}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect(url_for('admin'))
        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notices ORDER BY timestamp DESC')
    notices = cursor.fetchall()
    conn.close()
    return render_template('index.html', notices=notices)

@app.route('/admin')
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM notices ORDER BY timestamp DESC')
    notices = cursor.fetchall()
    conn.close()
    return render_template('admin.html', notices=notices)

@app.route('/notices', methods=['POST'])
def add_notice():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']
    title = request.form['title']

    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join("static/uploads", filename)
        file.save(file_path)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO notices (title, file_path, file_type) VALUES (%s, %s, %s)', 
                       (title, file_path, filename.rsplit('.', 1)[1].lower()))
        conn.commit()
        conn.close()

        socketio.emit('update_notices', {'data': 'New notice added'})
        return redirect(url_for('admin'))

    return "Invalid file type"

@app.route('/notices/<int:notice_id>/delete', methods=['POST'])
def delete_notice(notice_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notices WHERE id = %s', (notice_id,))
    conn.commit()
    conn.close()

    socketio.emit('update_notices', {'data': 'Notice deleted'})
    return redirect(url_for('admin'))

if __name__ == '__main__':
    socketio.run(app, debug=True)
