import os
import time
import socket
import json


class FileSynchronization:
    def __init__(self, target_ip='192.168.100.11', interface='', port=5207, backlog=128):
        self.target_ip = target_ip
        self.interface = interface
        self.port = port
        self.backlog = backlog

        self.tcp_server_socket = None
        self.tcp_client_socket = None

        self.show_hidden_files = False
        self.files_path = None
        self.file_info = None

        self.server_file_info = None

    def set_target_ip(self, target_ip):
        self.target_ip = target_ip

    def set_interface(self, interface):
        self.interface = interface

    def set_port(self, port):
        self.port = port

    def create_server_socket(self):
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server_socket.bind((self.interface, self.port))
        tcp_server_socket.listen(self.backlog)
        self.tcp_server_socket = tcp_server_socket
        return self.tcp_server_socket

    def create_client_socket(self):
        self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_client_socket.connect((self.target_ip, self.port))
        return self.tcp_client_socket

    def get_all_file(self, path):
        file_list = os.listdir(path)
        for file in file_list:
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                self.get_all_file(file_path)
            if file_path.split('/')[-1].startswith('.') and not self.show_hidden_files:
                continue
            self.files_path.append(file_path)

    def get_files_path(self, path):
        self.files_path = []
        self.get_all_file(path)

    def check_modified_time(self, path=None):
        if not path:
            path = self.files_path
        file_dict = {'file name': [], 'modified time': [], 'create time': []}
        for file in path:
            file_name = file.split('/')[-1]
            mtime = time.localtime(os.path.getmtime(file))
            ctime = time.localtime(os.path.getctime(file))
            file_dict['file name'].append(file_name)
            file_dict['modified time'].append(time.strftime('%Y%m%d%H%M', mtime))
            file_dict['create time'].append(time.strftime('%Y%m%d%H%M', ctime))
        self.file_info = file_dict

    def deal_client_request(self, ip_port, client_socket):
        print('{} connnected.'.format(ip_port))
        request_type = client_socket.recv(1024).decode('utf-8')
        if request_type == 'file info':
            self.get_files_path('../../BillCalculator/BillCalculator/data')
            self.check_modified_time()
            client_socket.send(json.dumps(self.file_info).encode('utf-8'))
        elif request_type.split(':')[0] == 'request':
            file_name = request_type.split(':')[1]
            if file_name in self.file_info['file name']:
                client_socket.send('OK'.encode('utf-8'))
                index = self.file_info['file name'].index(file_name)
                with open(self.files_path[index], 'r') as f:
                    while True:
                        data = f.read(1024)
                        if data:
                            client_socket.send(data.encode('utf-8'))
                        else:
                            print('{} has been sent!'.format(file_name))
                            break
            else:
                client_socket.send('Bad'.encode('utf-8'))
            client_socket.close()
        elif request_type.split(':')[0] == 'response':
            file_name = request_type.split(':')[1]
            if file_name in self.file_info['file name']:
                client_socket.send('Yes'.encode('utf-8'))
                index = self.file_info['file name'].index(file_name)
                with open(self.files_path[index], 'w') as f:
                    while True:
                        data = client_socket.recv(1024)
                        if data:
                            f.write(data.decode('utf-8'))
                        else:
                            print('{} has been updated!'.format(file_name))
                            break
            else:
                print('{} is not allowed to be sent from client!'.format(file_name))
            client_socket.close()
        else:
            print('Unknown request!')
        client_socket.close()

    def get_server_files_info(self):
        client_socket = self.create_client_socket()
        client_socket.send('file info'.encode('utf-8'))
        self.server_file_info = json.loads(client_socket.recv(1024).decode('utf-8'))
        client_socket.close()

    def process_files_info(self):
        self.file_info['operation'] = ['nochange'] * len(self.file_info['file name'])
        for i, (file_name, modified_time) in enumerate(
                zip(self.file_info['file name'], self.file_info['modified time'])):
            if file_name in self.server_file_info['file name']:
                index = self.server_file_info['file name'].index(file_name)
                if int(modified_time) < int(self.server_file_info['modified time'][index]):
                    self.file_info['operation'][i] = 'request'
                else:
                    self.file_info['operation'][i] = 'response'

    def generate_client_request(self):
        for i, operation in enumerate(self.file_info['operation']):
            if operation == 'request':
                file_name = self.file_info['file name'][i]
                request_socket = self.create_client_socket()
                request_socket.send('request:{}'.format(file_name).encode('utf-8'))
                is_available = request_socket.recv(1024).decode('utf-8')
                if is_available == 'OK':
                    with open(self.files_path[i], 'w') as f:
                        while True:
                            data = request_socket.recv(1024).decode('utf-8')
                            if data:
                                f.write(data)
                            else:
                                print('{} has been updated!'.format(file_name))
                                break
                else:
                    print('no file named {} in server found!'.format(file_name))
                request_socket.close()
            elif operation == 'response':
                file_name = self.file_info['file name'][i]
                response_socket = self.create_client_socket()
                response_socket.send('response:{}'.format(file_name).encode('utf-8'))
                is_allowable = response_socket.recv(1024).decode('utf-8')
                if is_allowable == 'Yes':
                    with open(self.files_path[i], 'r') as f:
                        while True:
                            data = f.read(1024)
                            if data:
                                response_socket.send(data.encode('utf-8'))
                            else:
                                print('{} has been sent!'.format(file_name))
                                break
                else:
                    print('{} is not allowed to be sent to server!'.format(file_name))
                response_socket.close()

    def delete_old_files(self):
        pass

    def copy_new_files(self):
        pass

    def copy_to_clipboard(self):
        pass

    def paste_from_clipboard(self):
        pass


if __name__ == '__main__':
    FS = FileSynchronization()
    FS.get_files_path('../../BillCalculator/BillCalculator/data')
    FS.check_modified_time()
    # print(str(FS.file_info))
    TCP_Server = FS.create_server_socket()
    client_socket, ip_port = TCP_Server.accept()
    print(ip_port)

    client_socket.send(json.dumps(FS.file_info).encode('utf-8'))
    remote_file_info = json.loads(client_socket.recv(1024).decode('utf-8'))
    local_file_info = FS.file_info

    local_file_info['to delete'] = [None]*len(local_file_info['file name'])
    for i, (file_name, modified_time) in enumerate(zip(local_file_info['file name'], local_file_info['modified time'])):
        print(file_name)
        print(remote_file_info['file name'])
        if file_name in remote_file_info['file name']:
            index = remote_file_info['file name'].index(file_name)
            if int(modified_time) < int(remote_file_info['modified time'][index]):
                local_file_info['to delete'][i] = True
            else:
                local_file_info['to delete'][i] = False
    print('local file info: {}'.format(local_file_info))
    print('remote file info: {}'.format(remote_file_info))
    b = sorted(zip(local_file_info['file name'], local_file_info['modified time'], local_file_info['to delete']),
               key=lambda x: x[0])
    c = {'file name': [], 'modified time': [], 'to delete': []}
    for fn, mt, td in b:
        c['file name'].append(fn)
        c['modified time'].append(mt)
        c['to delete'].append(td)
    sorted_file_info = c
    print(sorted_file_info)

    for i, to_delete in enumerate(sorted_file_info['to delete']):
        if to_delete is True:
            time.sleep(0.5)
            print('delete {}'.format(sorted_file_info['file name'][i]))
            idx = local_file_info['file name'].index(sorted_file_info['file name'][i])
            client_socket.send('request:{}'.format(sorted_file_info['file name'][i]).encode('utf-8'))
            if client_socket.recv(1024).decode('utf-8') == 'response':
                with open(FS.files_path[idx], 'w') as f:
                    while True:
                        data = client_socket.recv(1024)
                        if data:
                            f.write(data.decode('utf-8'))
                        else:
                            print('{} has been updated!'.format(sorted_file_info['file name'][i]))
                            break
        elif to_delete is False:
            time.sleep(0.5)
            data = client_socket.recv(1024).decode('utf-8')
            print(data)
            if data.startswith('request') and data.split(':')[-1] == sorted_file_info['file name'][i]:
                idx = local_file_info['file name'].index(sorted_file_info['file name'][i])
                client_socket.send('response'.encode('utf-8'))
                with open(FS.files_path[idx], 'r') as f:
                    while True:
                        file_data = f.read(1024)
                        if file_data:
                            client_socket.send(file_data.encode('utf-8'))
                        else:
                            print('{} has been send!'.format(sorted_file_info['file name'][i]))
                            break

    client_socket.close()
