import requests
import json

# 服务器地址
BASE_URL = 'http://127.0.0.1:8000/api'

def test_admin_login():
    """测试新的超级管理员登录"""
    print("\n===== 测试新的超级管理员登录 =====")
    
    # 登录数据 - 使用刚刚创建的超级管理员账户
    login_data = {
        "username": "wstier477",
        "password": "wstier477"  # 请替换为您实际设置的密码
    }
    
    # 发送请求
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    
    # 打印结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    return response.json()

if __name__ == "__main__":
    try:
        test_admin_login()
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器。请确保Django服务器正在运行。")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}") 