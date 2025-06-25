import socket      # 引入 socket 库，负责网络通信功能
import threading   # 引入 threading 库，实现多线程处理多个客户端连接

def client_handler(connection, client_address):
    """
    处理单个客户端的通信请求
    参数:
        connection: 服务器与客户端之间的连接套接字
        client_address: 客户端的地址信息（IP, 端口）
    """
    print(f"[连接建立] 客户端 {client_address} 已连接")
    expected_blocks = None  # 用于存储客户端初始化时发送的块数

    try:
        while True:
            # 先接收4字节协议头，指示后续操作类型
            command = connection.recv(4).decode()
            if not command:
                # 如果没有接收到数据，说明客户端已关闭连接
                break

            if command == "INIT":
                # 初始化命令，接收接下来的4字节数据，表示数据块总数
                data_len_bytes = connection.recv(4)
                expected_blocks = int(data_len_bytes.decode())
                print(f"[初始化] 收到客户端初始化，数据块数={expected_blocks}")
                # 回复同意标志，告诉客户端初始化成功
                connection.sendall(b"AGRE")

            elif command == "REQ_":
                # 请求命令，接收4字节长度信息，说明接下来接收的数据块大小
                length_bytes = connection.recv(4)
                length = int(length_bytes.decode())
                # 按照长度接收数据块内容
                data_bytes = b""
                while len(data_bytes) < length:
                    more_data = connection.recv(length - len(data_bytes))
                    if not more_data:
                        # 如果数据提前断开，退出循环
                        break
                    data_bytes += more_data

                data_str = data_bytes.decode()
                # 对接收到的字符串进行反转
                reversed_str = data_str[::-1]
                print(f"[数据处理] 接收数据块：{data_str}")

                # 发送响应：先发送4字节响应头
                connection.sendall(b"ANS_")
                # 再发送4字节长度（字符串形式，左侧补0凑满4位）
                reversed_len_str = str(len(reversed_str)).zfill(4)
                connection.sendall(reversed_len_str.encode())
                # 最后发送反转后的数据内容
                connection.sendall(reversed_str.encode())

    except Exception as err:
        # 捕获异常，打印错误信息
        print(f"[错误] 与客户端 {client_address} 通信出现异常: {err}")
    finally:
        # 无论异常与否，确保关闭连接
        connection.close()
        print(f"[断开连接] 客户端 {client_address} 已断开")

def run_server():
    """
    主函数：创建 TCP 服务器，监听端口并接收客户端连接
    """
    SERVER_HOST = "0.0.0.0"  # 绑定所有可用网卡地址
    SERVER_PORT = 12345       # 监听端口号

    # 创建 TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # 绑定IP地址和端口
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        # 开始监听，允许等待连接队列大小默认
        server_socket.listen()
        print(f"[启动] 服务器正在端口 {SERVER_PORT} 等待客户端连接...")

        # 循环接收客户端连接
        while True:
            client_conn, client_addr = server_socket.accept()  # 阻塞等待客户端连接
            # 为每个客户端创建一个独立线程进行服务，避免阻塞其他连接
            threading.Thread(target=client_handler, args=(client_conn, client_addr)).start()

if __name__ == "__main__":
    run_server()
