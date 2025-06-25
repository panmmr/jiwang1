import socket      # 网络通信模块
import argparse    # 解析命令行参数
import random     # 用于生成随机分块长度
import os         # 处理文件路径相关功能

def split_file_into_chunks(file_path, min_len, max_len):
    """
    将文件内容按随机长度分块，长度在[min_len, max_len]之间
    """
    with open(file_path, 'r') as f:
        content = f.read()
    chunks = []
    pos = 0
    while pos < len(content):
        length = random.randint(min_len, max_len)
        chunks.append(content[pos:pos+length])
        pos += length
    return chunks

def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="客户端程序：分块发送文件并接收反转结果")
    parser.add_argument('--serverIP', required=True, help='服务器IP地址')
    parser.add_argument('--serverPort', type=int, required=True, help='服务器端口号')
    parser.add_argument('--file', required=True, help='待处理文件路径')
    parser.add_argument('--Lmin', type=int, required=True, help='最小分块长度')
    parser.add_argument('--Lmax', type=int, required=True, help='最大分块长度')
    args = parser.parse_args()

    # 将文件分割成多个随机长度的数据块
    chunks = split_file_into_chunks(args.file, args.Lmin, args.Lmax)
    final_reversed = ''  # 用于累计服务器返回的所有反转字符串

    # 创建 TCP 连接
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        client_sock.connect((args.serverIP, args.serverPort))

        # 发送初始化请求，通知服务器分块数
        client_sock.sendall(b'INIT')  # 发送初始化命令标识
        client_sock.sendall(str(len(chunks)).zfill(4).encode())  # 4位长度字符串，告知块数

        # 接收服务器确认
        if client_sock.recv(4) != b'AGRE':
            print("[-] 服务器未同意初始化请求")
            return

        # 依次发送各块，等待并打印服务器返回的反转结果
        for idx, chunk in enumerate(chunks):
            client_sock.sendall(b'REQ_')  # 发送请求处理命令标识
            client_sock.sendall(str(len(chunk)).zfill(4).encode())  # 4字节长度
            client_sock.sendall(chunk.encode())  # 发送数据块

            # 接收响应头并验证
            if client_sock.recv(4) != b'ANS_':
                print("[-] 服务器响应格式错误")
                return

            # 接收反转字符串长度
            resp_len = int(client_sock.recv(4).decode())
            # 接收反转数据内容
            reversed_chunk = client_sock.recv(resp_len).decode()
            print(f"{idx + 1}: {reversed_chunk}")
            final_reversed += reversed_chunk

    # 写入文件，命名为 原文件名_reversed.txt
    base_name = os.path.splitext(args.file)[0]
    output_path = base_name + "_reversed.txt"
    with open(output_path, 'w') as out_file:
        out_file.write(final_reversed)

    print(f"[+] 反转后的内容已保存至 {output_path}")

if __name__ == "__main__":
    main()
