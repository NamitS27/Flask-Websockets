from flask import Flask, render_template
from flask_socketio import SocketIO, join_room

from datetime import datetime
import redis
from dateutil.relativedelta import relativedelta as rd
import os
from dotenv import load_dotenv
from threading import Thread
import time
import heapq

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
socket_ = SocketIO(app, async_mode='gevent')

client_queue = []


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
    # last step would be to remove the client from the client queue as well as from the redis


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
    return ' '.join('{} {}'.format(getattr(readable_time, k), k if getattr(readable_time,k) > 1 else k[:len(k)-1]) for k in intervals if getattr(readable_time, k))


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


def heartbeat_handler(socket_):
    '''
    Handles the dynamic heartbeat of multiple clients.
    Based on the priority of the client whose heartbeat is the earliest, it will be the one to be removed from the queue.
    and accordinly the heartbeat will be sent to the client.

    This can also be achieved by using RabbitMQ asynchronous messaging (kinda serving like a webhook).
    '''
    while True:
        if len(client_queue) > 0:
            curr_job = heapq.heappop(client_queue)
            if curr_job[0] > datetime.now().timestamp():
                heapq.heappush(client_queue, curr_job)
                time.sleep(curr_job[0] - datetime.now().timestamp())
            else:
                t = Thread(target=lambda: socket_.emit('ping', 'Connected', room=curr_job[1]))
                t.start()
                heapq.heappush(client_queue, (datetime.now().timestamp() + curr_job[2], curr_job[1], curr_job[2]))


hbt_thread = Thread(target=heartbeat_handler, args=(socket_,))
hbt_thread.start()


@socket_.on('heartbeat')
def heartbeat(data):
    socket_id = data['socket_id']
    heartbt = int(data['heartbeat'])
    job = (datetime.now().timestamp() + heartbt, socket_id, heartbt)
    heapq.heappush(client_queue, job)
    # The following code is for the condition when there are suppose 4 clients connected to the server.
    # The least of them has a heartbeat of lets say 1 hour and a new client request to have a heartbeat of 5 minutes,
    # then we will have to wait for 1 hour and then send the ping to the new client. Hence for the same, we can
    # call the interrupt for the thread which will ultimately start running again and we can send the ping to the new client.
    # As python does not have a mechanism to interrupt a thread, we can use the following psuedocode to do the same.
    # if (job == client_queue[0]):
    #     hbt_thread.interrupt()


if __name__ == '__main__':
    socket_.run(app, port=os.getenv('PORT') or 8000, debug=os.getenv('DEBUG') == 'True')
