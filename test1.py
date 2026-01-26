# test1.py - 简单的联网测试脚本
import requests
from datetime import datetime

def main():
    # 获取当前时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 联网请求测试接口
    response = requests.get("https://httpbin.org/get")
    # 打印结果
    print(f"[{now}] 脚本运行成功！响应内容：")
    print(response.json()["origin"])  # 打印请求的IP地址

if __name__ == "__main__":
    main()


    
