from chat_socket import Client


def start_client(host: str, port: int) -> None:
    client = Client(host, port)
    conn = client.set_connection()
    client.echo(conn)


if __name__ == '__main__':
    start_client('127.0.0.1', 12345)
