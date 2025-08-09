import ssl
import socket

# 读取 IP 列表
with open('./source.txt', 'r') as f:
    ip_list = [line.strip() for line in f if line.strip()]

# 读取域名
with open('./config.txt', 'r') as f:
    domain = f.read().strip()

results = []

for ip in ip_list:
    try:
        # 建立 socket 连接并包裹为 SSL
        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=domain  # SNI
        )
        conn.settimeout(5)
        conn.connect((ip, 443))

        # 发送 HEAD 请求
        request = f"HEAD / HTTP/1.1\r\nHost: {domain}\r\nUser-Agent: {domain}\r\nConnection: close\r\n\r\n"
        conn.send(request.encode())

        # 读取响应头
        response = b""
        while True:
            data = conn.recv(4096)
            if not data:
                break
            response += data
        conn.close()

        # 判断是否包含 200 OK
        header_text = response.decode(errors='ignore')
        if "HTTP/1.1 200 OK" in header_text:
            print(f"[✔] {ip} 有效")
            results.append(ip)
        else:
            print(f"[×] {ip} 无效")

    except Exception as e:
        print(f"[!] {ip} 连接失败: {e}")

# 保存有效结果
with open('./results.txt', 'w') as f:
    for ip in results:
        f.write(ip + '\n')

print(f"\n✅ 检测完成，共发现 {len(results)} 个可用 IP。结果已写入 results.txt")
