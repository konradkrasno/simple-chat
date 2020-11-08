import sys
from source_client import Client


def start_client(host: str, port: int) -> None:
    client = Client(host, port)
    conn = client.set_connection()
    client.echo(conn)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"usage {sys.argv[0]} <host> <port>")
        exit(1)
    host, port = sys.argv[1], int(sys.argv[2])
    start_client(host, port)
