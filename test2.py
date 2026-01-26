# test1.py - 简单的联网测试脚本（带日志文件输出）
import requests
from datetime import datetime

def main():
    # 获取当前时间（用于日志内容）
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 获取日期（用于日志文件名，按天分类）
    date_str = datetime.now().strftime("%Y-%m-%d")
    # 日志文件名
    log_file = f"{date_str}_run_log.txt"

    # 联网请求测试接口
    try:
        response = requests.get("https://httpbin.org/get")
        response.raise_for_status()  # 捕获HTTP请求错误
        ip_address = response.json()["origin"]
        
        # 要输出的内容
        log_content = f"[{now}] 脚本运行成功！请求IP：{ip_address}\n"
        
        # 1. 打印到控制台（保留原有功能）
        print(log_content)
        
        # 2. 追加写入到日志文件（a+ 模式：不存在则创建，存在则追加）
        with open(log_file, "a+", encoding="utf-8") as f:
            f.write(log_content)
            
    except Exception as e:
        # 捕获异常并写入文件
        error_content = f"[{now}] 脚本运行失败！错误信息：{str(e)}\n"
        print(error_content)
        with open(log_file, "a+", encoding="utf-8") as f:
            f.write(error_content)

if __name__ == "__main__":
    main()
