from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # SQLiteデータベースのURL
socketio = SocketIO(app)
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

users = {
    'user1': 'pass1',
    'user2': 'pass2'
}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('chat'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))
    messages = Message.query.all()
    return render_template('chat.html', username=session['username'], messages=messages)

@socketio.on('message')
def handle_message(data):
    sender = data['sender']
    msg = data['msg']
    new_message = Message(sender=sender, content=msg)
    db.session.add(new_message)
    db.session.commit()
    emit('message', {'sender': sender, 'msg': msg}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
