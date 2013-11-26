from celery import task
from .websockify import WebSocketProxy

@task
def start_websock(target_port, listen_port):
    server = WebSocketProxy(
            target_host='localhost',
            target_port=target_port,
            listen_host='*',
            listen_port=listen_port,
            )
    server.start_server()
