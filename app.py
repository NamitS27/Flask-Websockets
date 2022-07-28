from flask import Flask, render_template
from flask_socketio import SocketIO, join_room

from datetime import datetime
import redis
from dateutil.relativedelta import relativedelta as rd
import os
from dotenv import load_dotenv

load_dotenv()

redis_host = os.getenv('REDIS_HOST') or "localhost"
redis_port = os.getenv('REDIS_PORT') or 6379
redis_password = os.getenv('REDIS_PASSWORD')

# connecting to redis
r = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password,
    decode_responses=True
)
r.flushall()
'''
Note: As the redis is an in-memory database, the number of entries is restricted to the memory available in the system.
Taking this into consideration, and assuming number of clients can be huge, we will move to different storage mechanism.
Considering redis, we can restrict the size allocated to redis through its configuration and along with that, we can keep
and expiry mechanism to the key-value pair in place.
'''


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
    # calculate the number of clients connected to the server
    num_clients = int(r.get('num_clients') or 0) + 1
    r.set('num_clients', num_clients) # set the latest value of connected clients


@socket_.on('join')
def join(id):
    # make the client join the room with the same id as the socket id is unique
    join_room(id)
    socket_.emit('ping', 'Connected', room=id)
    r.set(id, datetime.now().timestamp())


@socket_.on('disconnect')
def disconnect():
    print('Client disconnected!')
    # calculate the number of clients connected to the server
    num_clients = int(r.get('num_clients')) - 1
    r.set('num_clients', num_clients) # set the latest value of connected clients


@socket_.on('server_time')
def server_time(id):
    now = datetime.now()
    timestamp = now.strftime('%b %d, %Y %I:%M %p')
    # calculate and send the current server time to the requested client
    socket_.emit(
        'server_time',
        {'timestamp': timestamp},
        room=id
    )


@socket_.on('num_clients')
def num_clients(id):
    # fetch and send the "number of clients connected to the server"
    socket_.emit(
        'num_clients',
        r.get('num_clients'),
        room=id
    )


def format_timespan(seconds):
    intervals = ['days', 'hours', 'minutes', 'seconds']
    readable_time = rd(seconds=seconds)
    return ' '.join('{} {}'.format(getattr(readable_time, k), k) for k in intervals if getattr(readable_time, k))


@socket_.on('client_time')
def client_time(id):
    # calculate the time interval since the client connected
    # to the server and send it to the client
    secs = (datetime.now().timestamp() - float(r.get(id)))
    socket_.emit(
        'client_time',
        {'connection_time': format_timespan(round(secs))},
        room=id
    )


@socket_.on('ping')
def ping(id):
    socket_.emit('ping', 'Connected', room=id)


'''
The following code can be uncommented in order to send a specific message to all clients after a specific time interval.
The only disadvantage of this approach is that the message will be tried to sent to all clients, even if they are
not connected to the server. Also, a thread will be created for each client, which will be consuming CPU resources.

from threading import Thread
def ping():
    # A function which sends a ping to all clients every 60 seconds
    while True:
        print('Sending ping to all clients...')
        socket_.emit('ping', 'Connected', broadcast=True)
        socket_.sleep(60)

t = Thread(target=ping)
t.start()
'''

if __name__ == '__main__':
    socket_.run(app, port=os.getenv('PORT') or 8000, debug=os.getenv('DEBUG') == 'True')
