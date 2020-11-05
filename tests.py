import pytest
import threading
import time

from chat_socket import Client
from server import start_server, HOST, PORT



@pytest.fixture
def server() -> None:
    thread = threading.Thread(target=start_server, args=(HOST, PORT, True,))
    thread.start()
    time.sleep(0.00001)


def test_server(server: pytest.fixture) -> None:
    connections = []
    client_1 = Client(HOST, PORT)
    conn_1 = client_1.set_connection()
    connections.append(conn_1)

    client_2 = Client(HOST, PORT)
    conn_2 = client_2.set_connection()
    connections.append(conn_2)

    client_3 = Client(HOST, PORT)
    conn_3 = client_3.set_connection()
    connections.append(conn_3)

    # greeting
    # client 1
    assert conn_1.recv(1024) == b"Connected to the server.\nGive your nick name: "
    conn_1.send(b"Freddie")
    assert conn_1.recv(1024) == b"hello Freddie"
    # client 2
    assert conn_2.recv(1024) == b"Connected to the server.\nGive your nick name: "
    conn_2.send(b"Jim")
    assert conn_2.recv(1024) == b"hello Jim"
    # client 3
    assert conn_3.recv(1024) == b"Connected to the server.\nGive your nick name: "
    conn_3.send(b"Mick")
    assert conn_3.recv(1024) == b"hello Mick"

    # conversation
    conn_1.send(b"what's up?")
    assert conn_1.recv(1024) == b"Freddie: what's up?"
    assert conn_2.recv(1024) == b"Freddie: what's up?"
    assert conn_3.recv(1024) == b"Freddie: what's up?"

    conn_2.send(b"it's fine")
    assert conn_1.recv(1024) == b"Jim: it's fine"
    assert conn_2.recv(1024) == b"Jim: it's fine"
    assert conn_3.recv(1024) == b"Jim: it's fine"

    conn_3.send(b"it's boring")
    assert conn_1.recv(1024) == b"Mick: it's boring"
    assert conn_2.recv(1024) == b"Mick: it's boring"
    assert conn_3.recv(1024) == b"Mick: it's boring"

    # stop server
    client_1.stop_server(conn_1)
    client_1.set_connection()
