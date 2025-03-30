from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import json
import tempfile
import re
import numpy as np
import cv2
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import datetime
from django.conf import settings
from .models import Face
from user_management.utils import api_response  # 导入api_response工具函数

# Create your views here.

# 人脸分析器将在 apps.py 的 ready() 方法中初始化
app = None

@csrf_exempt
def insert_face(request):
    """插入单个人脸"""
    if request.method != 'POST':
        return api_response(
            code=400,
            message="只支持POST请求",
            data=None
        )
    
    if 'image' not in request.FILES:
        return api_response(
            code=400,
            message="未提供图像文件",
            data=None
        )
        
    image_file = request.FILES['image']
    filename = image_file.name
    
    # 解析文件名获取人名和ID
    name_id = os.path.splitext(filename)[0]  # 移除扩展名
    match = re.search(r'(.+)_(\d+)', name_id)
    if match:
        name = match.group(1)
        face_id = int(match.group(2))
    else:
        name = name_id
        face_id = 1

    # 测试模式或insightface未初始化
    if app is None:
        # 返回模拟成功响应
        return api_response(
            code=200, 
            message=f"测试模式：成功添加{name}的人脸", 
            data={
                "id": face_id,
                "name": name
            }
        )
    
    # 真实模式
    try:
        # 读取图像数据
        img_data = image_file.read()
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 检测人脸
        faces = app.get(img)
        
        if len(faces) == 0:
            return api_response(
                code=400,
                message="未检测到人脸",
                data=None
            )
        
        if len(faces) > 1:
            return api_response(
                code=400,
                message=f"检测到多个人脸({len(faces)}个)，请提供单人照片",
                data=None
            )
        
        # 获取人脸特征
        face = faces[0]
        feat = face.normed_embedding
        
        # 保存到数据库
        face_obj, created = Face.objects.update_or_create(
            id=face_id,
            defaults={
                'name': name,
                'feat': feat.tobytes()
            }
        )
        
        return api_response(
            code=200,
            message=f"成功{'添加' if created else '更新'}{name}的人脸",
            data={
                "id": face_id,
                "name": name,
                "created": created
            }
        )
        
    except Exception as e:
        return api_response(
            code=500,
            message=f"处理人脸失败: {str(e)}",
            data=None
        )

@csrf_exempt
def batch_insert_faces(request):
    """批量插入人脸"""
    if request.method != 'POST':
        return api_response(
            code=400,
            message="只支持POST请求",
            data=None
        )
    
    # 测试模式或insightface未初始化
    if app is None:
        # 返回模拟成功响应
        return api_response(
            code=200,
            message="测试模式：批量插入人脸功能暂未实现",
            data={
                "success": [],
                "failed": []
            }
        )
    
    # 真实模式实现批量插入（可根据实际需求扩展）
    # ...

    return api_response(
        code=501,
        message="批量插入人脸功能尚未实现",
        data=None
    )

@csrf_exempt
def check_attendance(request):
    """检查考勤"""
    if request.method != 'POST':
        return api_response(
            code=400,
            message="只支持POST请求",
            data=None
        )
    
    if 'image' not in request.FILES:
        return api_response(
            code=400,
            message="未提供图像文件",
            data=None
        )
    
    # 获取图片文件名
    image_file = request.FILES['image']
    file_name = os.path.splitext(image_file.name)[0]
    
    # 测试模式或insightface未初始化
    if app is None:
        # 创建模拟考勤记录
        attendance_records = [
            {'id': 1, 'name': '张三', 'present': 1, 'confidence': 0.85},
            {'id': 2, 'name': '李四', 'present': 0, 'confidence': 0.45},
            {'id': 3, 'name': '王五', 'present': 1, 'confidence': 0.92}
        ]
        
        # 使用当前时间作为考勤文件名
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_{current_time}.txt"
        
        # 创建文件内容
        file_content = ""
        for record in attendance_records:
            file_content += f"{record['id']} {record['name']} {record['present']}\n"
        
        # 确保目录存在
        attendance_dir = os.path.join(settings.MEDIA_ROOT, 'attendance_records')
        os.makedirs(attendance_dir, exist_ok=True)
        
        # 将文件存储到默认存储位置
        path = default_storage.save(f'attendance_records/{filename}', ContentFile(file_content.encode('utf-8')))
        
        # 统计出席和缺席人数
        present_count = sum(1 for record in attendance_records if record['present'] == 1)
        absent_count = len(attendance_records) - present_count
        
        return api_response(
            code=200,
            message=f"测试模式：已生成考勤记录，出席人数：{present_count}，缺席人数：{absent_count}",
            data={
                "file_path": path,
                "attendance_records": attendance_records,
                "stats": {
                    "total": len(attendance_records),
                    "present": present_count,
                    "absent": absent_count
                }
            }
        )
    
    # 真实模式
    try:
        # 读取图像数据
        img_data = image_file.read()
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 检测人脸
        faces = app.get(img)
        
        if len(faces) == 0:
            return api_response(
                code=400,
                message="未检测到人脸",
                data=None
            )
        
        # 获取所有已知人脸
        known_faces = Face.objects.all()
        if not known_faces:
            return api_response(
                code=404,
                message="数据库中没有已知人脸数据",
                data=None
            )
        
        # 构建人脸特征矩阵
        known_feats = []
        for face_obj in known_faces:
            feat = np.frombuffer(face_obj.feat, dtype=np.float32)
            known_feats.append(feat)
        
        known_feats = np.array(known_feats)
        
        # 创建考勤记录
        attendance_records = []
        recognized_faces = []
        
        for face in faces:
            feat = face.normed_embedding
            
            # 计算相似度
            sim = np.dot(known_feats, feat)
            best_idx = np.argmax(sim)
            best_sim = sim[best_idx]
            
            # 阈值判断
            threshold = 0.5  # 可根据需要调整
            if best_sim > threshold:
                # 识别成功
                face_obj = known_faces[int(best_idx)]  # 将numpy的int64转换为Python的int
                attendance_records.append({
                    'id': face_obj.id,
                    'name': face_obj.name,
                    'present': 1,
                    'confidence': float(best_sim)
                })
                recognized_faces.append(face_obj)
            else:
                # 未能识别的人脸
                attendance_records.append({
                    'id': -1,
                    'name': "未知",
                    'present': 0,
                    'confidence': float(best_sim)
                })
        
        # 使用当前时间作为考勤文件名
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"attendance_{current_time}.txt"
        
        # 创建文件内容
        file_content = ""
        for record in attendance_records:
            file_content += f"{record['id']} {record['name']} {record['present']}\n"
        
        # 确保目录存在
        attendance_dir = os.path.join(settings.MEDIA_ROOT, 'attendance_records')
        os.makedirs(attendance_dir, exist_ok=True)
        
        # 将文件存储到默认存储位置
        path = default_storage.save(f'attendance_records/{filename}', ContentFile(file_content.encode('utf-8')))
        
        # 统计出席和缺席人数
        present_count = sum(1 for record in attendance_records if record['present'] == 1)
        absent_count = len(attendance_records) - present_count
        
        return api_response(
            code=200,
            message=f"已生成考勤记录，检测到{len(faces)}个人脸，识别出{present_count}人",
            data={
                "file_path": path,
                "attendance_records": attendance_records,
                "stats": {
                    "total": len(attendance_records),
                    "present": present_count,
                    "absent": absent_count
                }
            }
        )
        
    except Exception as e:
        return api_response(
            code=500,
            message=f"处理失败: {str(e)}",
            data=None
        )

@csrf_exempt
def download_attendance_file(request):
    """下载考勤记录文件"""
    if request.method != 'GET':
        return api_response(
            code=400,
            message="只支持GET请求",
            data=None
        )
    
    # 获取指定文件名
    filename = request.GET.get('filename', '')
    
    if not filename:
        return api_response(
            code=400,
            message="未指定文件名",
            data=None
        )
    
    file_path = f'attendance_records/{filename}'
    
    try:
        # 检查文件是否存在
        if default_storage.exists(file_path):
            # 读取文件内容
            file_content = default_storage.open(file_path).read()
            
            # 创建响应
            response = HttpResponse(file_content, content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        else:
            return api_response(
                code=404,
                message="文件不存在",
                data=None
            )
    except Exception as e:
        return api_response(
            code=500,
            message=f"下载失败: {str(e)}",
            data=None
        )
