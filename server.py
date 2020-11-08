import sys
from source_server import Server


def start_server(host: str, port: int, debug: bool = False) -> None:
    with Server(host, port, debug=debug) as server:
        server.bind()
        server.listen()
        server.echo()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage {sys.argv[0]} <host> <port>")
        exit(1)
    host, port = sys.argv[1], int(sys.argv[2])
    start_server(host, port, debug=True)
