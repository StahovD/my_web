from flask import Flask, render_template, redirect, url_for, flash, request, session
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

conn = sqlite3.connect('mein.db', check_same_thread=False)
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
email TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
conn.commit()

@app.route('/')
def index():
    cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')
    posts = cursor.fetchall()
    return render_template('index.html', posts=posts)

@app.route('/post/new', methods=['POST'])
def new_post():
    content = request.form['content']
    cursor.execute('INSERT INTO posts (content, user_id) VALUES (?,?)', (content, 1))
    conn.commit()
    flash('Пост створено успішно!')
    return redirect(url_for('index'))

@app.context_processor
def inject_current_user():
    user_id = session.get('user_id')
    if user_id:
        return {'current_user': cursor.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()}
    else:
        return {'current_user': None}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (request.form['username'], request.form['password'])).fetchone()
        if user:
            session['user_id'] = user['id']
            flash('Вхід успішний! Ласкаво просимо.')
            return redirect(url_for('index'))
        else:
            flash('Невірний логін або пароль. Спробуйте ще раз.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Вихід успішний! Повертайтеся знову.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?,?,?)', (request.form['username'], request.form['email'], request.form['password']))
        conn.commit()
        flash('Реєстрація успішна!')
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':

    app.run(debug=True)