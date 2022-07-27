from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room
from threading import Thread
import redis
import os

redis_host = os.getenv('REDIS_HOST') or "localhost"
redis_port = os.getenv('REDIS_PORT') or 6379
redis_password = os.getenv('REDIS_PASSWORD')

r = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True
)
r.flushall()


app = Flask(__name__)
socket_ = SocketIO(app)


@app.route('/')
def index():
    return render_template(
        'client.html'
    )


@socket_.on('connect')
def connect():
    print('Client connected!')
    num_clients = int(r.get('num_clients') or 0) + 1
    r.set('num_clients', num_clients, ex=1800)


@socket_.on('join')
def join(id):
    join_room(id)
    r.set(id, datetime.now().timestamp(), ex=1800)


@socket_.on('disconnect')
def disconnect(id):
    print('Client disconnected!')
    num_clients = int(r.get('num_clients')) - 1
    leave_room(id)
    r.set('num_clients', num_clients, ex=1800)


@socket_.on('server_time')
def server_time(id):
    now = datetime.now()
    timestamp = now.strftime('%b %d, %Y %I:%M %p')
    socket_.emit(
        'server_time',
        {'timestamp': timestamp},
        room=id
    )


@socket_.on('num_clients')
def num_clients(id):
    socket_.emit(
        'num_clients',
        r.get('num_clients'),
        room=id
    )


@socket_.on('client_time')
def client_time(id):
    print(id)
    secs = (datetime.now().timestamp() - float(r.get(id)))
    socket_.emit(
        'client_time',
        {'connection_time': round(secs)},
        room=id
    )


def ping():
    while True:
        socket_.emit('ping', 'Connected', broadcast=True)
        socket_.sleep(60)


t = Thread(target=ping)
t.start()


if __name__ == '__main__':
    socket_.run(app, port=os.getenv('PORT') or 8000)
