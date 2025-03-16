import requests
import json

# 服务器地址
BASE_URL = 'http://127.0.0.1:8000/api'

def test_register():
    """测试注册接口"""
    print("\n===== 测试注册接口 =====")
    
    # 注册数据
    register_data = {
        "username": "testuser",
        "password": "Test@123456",
        "email": "testuser@example.com",
        "role": "student",
        "name": "测试用户"
    }
    
    # 发送请求
    response = requests.post(f"{BASE_URL}/register/", json=register_data)
    
    # 打印结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    return response.json()

def test_login():
    """测试登录接口"""
    print("\n===== 测试登录接口 =====")
    
    # 登录数据
    login_data = {
        "username": "testuser",
        "password": "Test@123456"
    }
    
    # 发送请求
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    
    # 打印结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    return response.json()

def test_logout(token):
    """测试退出登录接口"""
    print("\n===== 测试退出登录接口 =====")
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 发送请求
    response = requests.post(f"{BASE_URL}/logout/", headers=headers)
    
    # 打印结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    return response.json()

def test_admin_login():
    """测试管理员登录"""
    print("\n===== 测试管理员登录 =====")
    
    # 登录数据
    login_data = {
        "username": "你你你",
        "password": "123456"
    }
    
    # 发送请求
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    
    # 打印结果
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    return response.json()

def run_tests():
    """运行所有测试"""
    try:
        # 测试注册
        register_result = test_register()
        
        # 测试登录
        login_result = test_login()
        
        # 如果登录成功，测试退出登录
        if login_result.get('code') == 200 and login_result.get('data', {}).get('token'):
            token = login_result['data']['token']
            test_logout(token)
        
        # 测试管理员登录
        test_admin_login()
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器。请确保Django服务器正在运行。")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    run_tests() 