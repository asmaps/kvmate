from huey.djhuey import task
from .websockify import WebSocketProxy

def start_websock(target_port, listen_port):
    server = WebSocketProxy(
            target_host='localhost',
            target_port=target_port,
            listen_host='*',
            listen_port=listen_port,
            verbose=True,
            daemon=False,
            run_once=False,
            )
    server.start_server()
