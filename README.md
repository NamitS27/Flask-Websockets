# Websockets (Multiple Clients & Server)

<p>
    <a style="text-decoration:none">
        <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">
    </a>
    <a style="text-decoration:none">
        <img src="https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white">
    </a>
    <a style="text-decoration:none">
        <img src="https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white">
    </a>
    <a style="text-decoration:none">
        <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white">
    </a>
    <a style="text-decoration:none">
        <img src="https://img.shields.io/badge/redis-%23DD0031.svg?&style=for-the-badge&logo=redis&logoColor=white">
    </a>
<p>

A simple server - client application connected and communicating through web sockets.

## Table of Contents
- [Overview](#overview)
- [Installation and Running](#installation-and-running)
- [Demo](#demo)


## Overview

The task consists of setting up a simple flask server and a client application that connects to the server through web sockets. The client can request the following things from the server:

- Current server timestamp.
- Number of clients connected to the server.
- Time since "this" client is connected to the server.

Along with this, the server should send a "Connected" message every 1 min to all the connected clients. Based on this, mutiple socket listeners were created.

The following are the server side listeners and client side emitters:
\# | Socket | Functionality |
| ------------- | ------------- |  ------------- |
1.| connect  | connects the client with the server  |
2.| join | joins the specific client to the room based on the socket-id  |
3.| disconnect | disconnects the client from the server |
4.| server_time  | fetches the server's current timestamp  |
5.| client_time  | fetches the time duration since the specific client was connected |
6.| num_clients  | fetches the number of clients connected to the server  |
7.| ping  | pings the server in order to check the connection  |

From the above list, #4, #5, #6 and #7 are also the server side emitters and client side listeners.

## Installation and Running

1. First step is to install the required dependencies.
    ```bash
    pip install -r requirements.txt
    ```
2. Next, run the server.
    ```bash
    python app.py
    ```

3. You can now open the webpage available at [localhost](http://localhost:8000/) in your browser.


> Before running the application, you can create a `.env` file which will contain the following details:
```bash
REDIS_HOST=xxxxx # redis host
REDIS_PORT=xxxxx # redis port number
REDIS_PASSWORD=xxxxx # password required to connect
PORT=xxxxx # port number to start the server on
DEBUG=True # debug mode
```


## Demo

Google Drive Link for the video: [Demo of communication of a server connected with 5 other clients.](https://drive.google.com/file/d/1BcbfrV957MiieminWQDpaTqEtHV6nLtS/view?usp=sharing)
