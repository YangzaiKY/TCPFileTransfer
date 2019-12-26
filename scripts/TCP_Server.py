import socket
import os
import threading


def deal_client_request(ip_port, service_client_socket):
    print("客户端连接成功", ip_port)

    file_list = os.listdir('../data')
    send_data = ''
    f_size = []
    for file in file_list:
        f_size.append(os.path.getsize(file))
        fmb = f_size[-1]/float(1024*1024)
        send_data += 'file name: {} file size: {:.4f}MB\n'.format(file, fmb)
    if send_data:
        service_client_socket.send(send_data.encode('utf-8'))
    else:
        service_client_socket.send('no file found!'.encode('utf-8'))
    options = service_client_socket.recv(1024)
    file_name = options.decode('utf-8')
    if file_name in file_list:
        with open(file_name, 'rb') as f:
            nums = f_size[file_list.index(file_name)] / 1024
            cnum = 0

            while True:
                file_data = f.read(1024)
                cnum = cnum + 1
                progress = cnum / nums * 100
                print("当前已下载：{:.2f}%".format(progress), end='\r')
                if file_data:
                    service_client_socket.send(file_data)
                else:
                    print("请求的文件数据发送完毕")
                    break
    else:
        print("can not find file！")
    service_client_socket.close()


if __name__ == '__main__':
    os.chdir('../data')
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_socket.bind(('', 3356))
    tcp_server_socket.listen(128)

    while True:
        service_client_socket, ip_port = tcp_server_socket.accept()
        print(id(service_client_socket))

        sub_thread = threading.Thread(target=deal_client_request, args=(ip_port, service_client_socket))
        sub_thread.start()
