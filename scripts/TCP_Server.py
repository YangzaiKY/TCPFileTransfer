import socket
import os
import threading


def deal_client_request(ip_port, service_client_socket):
    print("客户端连接成功", ip_port)

    file_name = service_client_socket.recv(1024)
    file_name_data = file_name.decode("utf-8")
    if os.path.exists(file_name_data):
        fsize = os.path.getsize(file_name_data)
        fmb = fsize/float(1024*1024)
        send_data = "文件名: {} 文件大小: {:.2f}MB".format(file_name_data, fmb)
        service_client_socket.send(send_data.encode("utf-8"))
        print("请求文件名: {} 文件大小: {:.2f}MB".format(file_name_data, fmb))

        options = service_client_socket.recv(1024)
        if options.decode("utf-8") == 'y':
            with open(file_name_data, 'rb') as f:
                nums = fsize / 1024
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
            print("取消下载！")
    else:
        print("下载的文件不存在！")
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
