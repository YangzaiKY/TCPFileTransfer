import socket


if __name__ == '__main__':
    tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = input('请输入服务器IP：')
    tcp_client_socket.connect((server_ip, 3356))

    file_name = input('请输入要下载的文件名：')
    file_name_data = file_name.encode('utf-8')
    tcp_client_socket.send(file_name_data)
    file_info = tcp_client_socket.recv(1024)
    info_decode = file_info.decode('utf-8')
    print(info_decode)
    file_size = float(info_decode.split(':')[2].split('MB')[0])
    file_size2 = file_size * 1024
    opts = input('是否下载?(y 确认 q 取消) ')
    if opts == 'q':
        print('下载取消！程序退出')
    else:
        print('正在下载 》》》')
        tcp_client_socket.send(b'y')

        with open('../' + file_name, 'wb') as file:
            cnum = 0

            while True:
                file_data = tcp_client_socket.recv(1024)

                if file_data:
                    file.write(file_data)
                    progress = cnum / file_size2 * 100
                    print('当前已下载: {:.2f}%'.format(progress), end='\r')
                    cnum = cnum + 1
                else:
                    print('下载结束！')
                    break
    tcp_client_socket.close()
