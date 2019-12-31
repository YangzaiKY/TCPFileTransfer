import threading
from FileSynchronization import FileSynchronization


if __name__ == '__main__':
    FS = FileSynchronization()

    Server = FS.create_server_socket()
    while True:
        client_socket, ip_port = Server.accept()

        threading.Thread(target=FS.deal_client_request, args=(ip_port, client_socket)).start()
