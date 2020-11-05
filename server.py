from chat_socket import Server

HOST = '127.0.0.1'
PORT = 12345


def start_server(host: str, port: int, debug: bool = False) -> None:
    with Server(host, port, debug=debug) as server:
        server.bind()
        server.listen()
        server.echo()


if __name__ == "__main__":
    start_server(HOST, PORT, debug=True)
