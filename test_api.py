#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os
from pprint import pprint

"""
API测试脚本
测试注智课业API系统的各个接口
"""

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api"

# 存储认证令牌
token = None
user_id = None
course_id = None
resource_id = None

# 辅助函数：打印响应
def print_response(response, title=None):
    if title:
        print("\n" + "=" * 50)
        print(f"测试: {title}")
        print("=" * 50)
    
    print(f"状态码: {response.status_code}")
    try:
        response_json = response.json()
        print("响应JSON:")
        pprint(response_json)
        return response_json
    except:
        print("响应文本:")
        print(response.text)
        return None

# 1. 用户注册接口测试
def test_register():
    print("\n" + "=" * 50)
    print("测试: 用户注册接口")
    print("=" * 50)
    
    url = f"{BASE_URL}/register/"
    data = {
        "username": "testuser",
        "password": "Test@123456",
        "email": "testuser@example.com",
        "role": "student",
        "name": "测试用户"
    }
    
    response = requests.post(url, json=data)
    return print_response(response)

# 2. 用户登录接口测试
def test_login():
    global token, user_id
    
    url = f"{BASE_URL}/login/"
    data = {
        "username": "testuser",
        "password": "Test@123456"
    }
    
    response = requests.post(url, json=data)
    response_data = print_response(response, "用户登录接口")
    
    if response_data and response_data.get("code") == 200:
        token = response_data.get("data", {}).get("token")
        user_id = response_data.get("data", {}).get("userId")
        print(f"获取到令牌: {token}")
        print(f"用户ID: {user_id}")
    
    return response_data

# 3. 获取用户资料接口测试
def test_get_user_profile():
    if not token:
        print("未登录，无法测试")
        return
    
    url = f"{BASE_URL}/users/profile/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    return print_response(response, "获取用户资料接口")

# 4. 更新用户资料接口测试
def test_update_user_profile():
    if not token:
        print("未登录，无法测试")
        return
    
    url = f"{BASE_URL}/users/profile/"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "phone": "13800138000"
    }
    
    response = requests.put(url, json=data, headers=headers)
    return print_response(response, "更新用户资料接口")

# 5. 获取课程列表接口测试
def test_get_courses():
    global course_id
    
    if not token:
        print("未登录，无法测试")
        return
    
    url = f"{BASE_URL}/courses/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    response_data = print_response(response, "获取课程列表接口")
    
    # 如果有课程，保存第一个课程ID用于后续测试
    if (response_data and response_data.get("code") == 200 and 
        response_data.get("data", {}).get("items") and 
        len(response_data["data"]["items"]) > 0):
        course_id = response_data["data"]["items"][0].get("course_id")
        print(f"获取到课程ID: {course_id}")
    
    return response_data

# 6. 获取课程详情接口测试
def test_get_course_detail():
    if not token or not course_id:
        print("未登录或无课程ID，无法测试")
        return
    
    url = f"{BASE_URL}/courses/{course_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    return print_response(response, "获取课程详情接口")

# 7. 获取课程资源列表接口测试
def test_get_course_resources():
    global resource_id
    
    if not token or not course_id:
        print("未登录或无课程ID，无法测试")
        return
    
    url = f"{BASE_URL}/courses/{course_id}/resources/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    response_data = print_response(response, "获取课程资源列表接口")
    
    # 如果有资源，保存第一个资源ID用于后续测试
    if (response_data and response_data.get("code") == 200 and 
        response_data.get("data", {}).get("items") and 
        len(response_data["data"]["items"]) > 0):
        resource_id = response_data["data"]["items"][0].get("id")
        print(f"获取到资源ID: {resource_id}")
    
    return response_data

# 8. 上传课程资源接口测试
def test_upload_course_resource():
    if not token or not course_id:
        print("未登录或无课程ID，无法测试")
        return
    
    url = f"{BASE_URL}/courses/{course_id}/resources/"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 创建测试文件
    test_file_path = "test_resource.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("这是一个测试资源文件\n")
    
    files = {
        "file": open(test_file_path, "rb")
    }
    data = {
        "name": "测试资源",
        "type": "document",
        "description": "这是通过API测试上传的资源文件"
    }
    
    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        response_data = print_response(response, "上传课程资源接口")
        
        # 如果上传成功，保存资源ID
        if response_data and response_data.get("code") == 200:
            global resource_id
            resource_id = response_data.get("data", {}).get("id")
            print(f"上传资源ID: {resource_id}")
        
        return response_data
    finally:
        # 关闭文件
        files["file"].close()
        # 删除测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

# 9. 获取资源详情接口测试
def test_get_resource_detail():
    if not token or not resource_id:
        print("未登录或无资源ID，无法测试")
        return
    
    url = f"{BASE_URL}/resources/{resource_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    return print_response(response, "获取资源详情接口")

# 10. 下载资源接口测试
def test_download_resource():
    if not token or not resource_id:
        print("未登录或无资源ID，无法测试")
        return
    
    url = f"{BASE_URL}/resources/{resource_id}/download/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print("\n" + "=" * 50)
    print("测试: 下载资源接口")
    print("=" * 50)
    
    print(f"状态码: {response.status_code}")
    
    # 检查是否是文件响应或JSON响应
    content_type = response.headers.get("Content-Type", "")
    if "application/json" in content_type:
        return print_response(response)
    else:
        print("文件下载成功！")
        print(f"Content-Type: {content_type}")
        print(f"Content-Length: {len(response.content)} bytes")
        print(f"Content-Disposition: {response.headers.get('Content-Disposition', 'N/A')}")
        return response

# 11. 删除资源接口测试
def test_delete_resource():
    if not token or not resource_id:
        print("未登录或无资源ID，无法测试")
        return
    
    url = f"{BASE_URL}/resources/{resource_id}/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(url, headers=headers)
    return print_response(response, "删除资源接口")

# 12. 用户退出登录接口测试
def test_logout():
    if not token:
        print("未登录，无法测试")
        return
    
    url = f"{BASE_URL}/logout/"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, headers=headers)
    return print_response(response, "用户退出登录接口")

if __name__ == "__main__":
    print("注智课业API接口测试")
    print("=" * 50)
    
    # 尝试注册新用户
    test_register()
    
    # 登录
    test_login()
    
    if token:
        # 用户相关接口测试
        test_get_user_profile()
        test_update_user_profile()
        
        # 课程相关接口测试
        test_get_courses()
        
        if course_id:
            test_get_course_detail()
            test_get_course_resources()
            
            # 资源相关接口测试
            test_upload_course_resource()
            
            if resource_id:
                test_get_resource_detail()
                test_download_resource()
                test_delete_resource()
        
        # 最后退出登录
        test_logout()
    
    print("\n所有测试完成！") 