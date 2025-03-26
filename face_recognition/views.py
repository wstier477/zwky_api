from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from .models import Face
import json
import tempfile
import re
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import datetime
from django.conf import settings

# Create your views here.

# 人脸分析器将在 apps.py 的 ready() 方法中初始化
app = None

def extract_face_feature(image_data):
    """从图像数据中提取人脸特征"""
    # 将图像数据转换为numpy数组
    np_arr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        return None, "无法解码图像"
        
    # 检测人脸
    faces = app.get(img)
    if not faces:
        return None, "未检测到人脸"
        
    # 获取人脸特征向量
    feat = np.array(faces[0].normed_embedding, dtype=np.float32)
    return feat, None

def parse_filename(filename):
    """从文件名中解析名字和ID
    假设格式为: 张三_001.jpg 或 zhangsan_001.jpg
    """
    name_id = os.path.splitext(filename)[0]  # 移除扩展名
    
    # 使用正则表达式匹配名字和ID
    match = re.search(r'(.+)_(\d+)', name_id)
    if match:
        name = match.group(1)
        face_id = int(match.group(2))
        return name, face_id
    
    # 如果没有ID，就只返回名字
    return name_id, None

@csrf_exempt
def insert_face(request):
    """插入单个人脸"""
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "只支持POST请求"})
    
    if 'image' not in request.FILES:
        return JsonResponse({"status": "error", "message": "未提供图像文件"})
        
    image_file = request.FILES['image']
    filename = image_file.name
    
    # 解析文件名获取人名和ID
    name, face_id = parse_filename(filename)
    
    # 读取图像数据
    image_data = image_file.read()
    
    # 提取人脸特征
    feat, error = extract_face_feature(image_data)
    if error:
        return JsonResponse({"status": "error", "message": error})
    
    try:
        # 保存到数据库
        if face_id:
            face = Face(id=face_id, name=name, feat=feat.tobytes())
        else:
            face = Face(name=name, feat=feat.tobytes())
        face.save()
        
        return JsonResponse({
            "status": "success", 
            "message": f"成功添加{name}的人脸", 
            "id": face.id
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"保存失败: {str(e)}"})

@csrf_exempt
def batch_insert_faces(request):
    """批量插入人脸"""
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "只支持POST请求"})
    
    if 'folder' not in request.FILES:
        return JsonResponse({"status": "error", "message": "未提供文件夹"})
    
    files = request.FILES.getlist('folder')
    
    results = {
        "success": [],
        "failed": []
    }
    
    for file in files:
        if not (file.name.endswith('.jpg') or file.name.endswith('.png')):
            results["failed"].append({"name": file.name, "reason": "非图像文件"})
            continue
            
        # 解析文件名获取人名和ID
        name, face_id = parse_filename(file.name)
        
        # 读取图像数据
        image_data = file.read()
        
        # 提取人脸特征
        feat, error = extract_face_feature(image_data)
        if error:
            results["failed"].append({"name": file.name, "reason": error})
            continue
            
        try:
            # 保存到数据库
            if face_id:
                face = Face(id=face_id, name=name, feat=feat.tobytes())
            else:
                face = Face(name=name, feat=feat.tobytes())
            face.save()
            
            results["success"].append({"name": name, "id": face.id})
        except Exception as e:
            results["failed"].append({"name": file.name, "reason": str(e)})
    
    return JsonResponse({
        "status": "success",
        "message": f"成功添加{len(results['success'])}个人脸，失败{len(results['failed'])}个",
        "details": results
    })

@csrf_exempt
def check_attendance(request):
    """检查图片中的人脸与数据库中的人脸比对，生成考勤记录"""
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "只支持POST请求"})
    
    if 'image' not in request.FILES:
        return JsonResponse({"status": "error", "message": "未提供图像文件"})
    
    # 读取图像数据
    image_file = request.FILES['image']
    image_data = image_file.read()
    
    # 获取图片文件名（不含扩展名）作为时间标识
    file_name = os.path.splitext(image_file.name)[0]
    
    # 转换为OpenCV格式
    np_arr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        return JsonResponse({"status": "error", "message": "无法解码图像"})
    
    # 检测图片中的人脸
    faces = app.get(img)
    if not faces:
        return JsonResponse({"status": "error", "message": "图片中未检测到人脸"})
    
    # 提取图片中所有人脸的特征向量
    detected_feats = np.array([face.normed_embedding for face in faces], dtype=np.float32)
    
    # 从数据库中获取所有人脸特征
    all_faces = Face.objects.all()
    
    # 初始化考勤记录
    attendance_records = {}
    for face_record in all_faces:
        attendance_records[face_record.id] = {
            'id': face_record.id,
            'name': face_record.name,
            'present': 0  # 默认为缺席
        }
    
    # 设置相似度阈值
    face_config = getattr(settings, 'FACE_RECOGNITION', {})
    similarity_threshold = face_config.get('SIMILARITY_THRESHOLD', 0.5)
    
    # 比对人脸
    for db_face in all_faces:
        # 将二进制数据转换回numpy数组
        db_feat = np.frombuffer(db_face.feat, dtype=np.float32)
        
        # 计算与图片中所有人脸的相似度
        for detected_feat in detected_feats:
            similarity = np.dot(detected_feat, db_feat)
            
            # 如果相似度大于阈值，则认为该人出席
            if similarity > similarity_threshold:
                attendance_records[db_face.id]['present'] = 1
                break
    
    # 使用当前时间作为考勤文件名
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"attendance_{current_time}.txt"
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp_file:
        # 写入考勤记录
        for record in attendance_records.values():
            temp_file.write(f"{record['id']} {record['name']} {record['present']}\n")
    
    # 读取临时文件内容
    with open(temp_file.name, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    # 删除临时文件
    os.unlink(temp_file.name)
    
    # 确保目录存在
    attendance_dir = os.path.join(settings.MEDIA_ROOT, 'attendance_records')
    os.makedirs(attendance_dir, exist_ok=True)
    
    # 将文件存储到默认存储位置
    path = default_storage.save(f'attendance_records/{filename}', ContentFile(file_content.encode('utf-8')))
    
    # 统计出席和缺席人数
    present_count = sum(1 for record in attendance_records.values() if record['present'] == 1)
    absent_count = len(attendance_records) - present_count
    
    return JsonResponse({
        "status": "success",
        "message": f"已生成考勤记录，出席人数：{present_count}，缺席人数：{absent_count}",
        "file_path": path,
        "attendance_records": list(attendance_records.values())
    })

@csrf_exempt
def download_attendance_file(request):
    """下载最新的考勤记录文件"""
    if request.method != 'GET':
        return JsonResponse({"status": "error", "message": "只支持GET请求"})
    
    # 获取指定文件名或最新的文件
    filename = request.GET.get('filename', '')
    
    if filename:
        # 使用指定的文件名
        file_path = f'attendance_records/{filename}'
    else:
        # 获取最新的文件
        attendance_dir = 'attendance_records/'
        files = default_storage.listdir(attendance_dir)[1]  # [1]表示文件列表
        if not files:
            return JsonResponse({"status": "error", "message": "未找到考勤记录文件"})
        
        # 按创建时间排序
        files.sort(reverse=True)
        file_path = f'{attendance_dir}{files[0]}'
    
    # 检查文件是否存在
    if not default_storage.exists(file_path):
        return JsonResponse({"status": "error", "message": f"文件 {file_path} 不存在"})
    
    # 读取文件内容（以二进制方式）
    file_content = default_storage.open(file_path, 'rb').read()
        
    # 尝试以UTF-8解码，然后再编码以确保正确的UTF-8格式
    try:
        text_content = file_content.decode('utf-8')
        file_content = text_content.encode('utf-8')
    except UnicodeDecodeError:
        # 如果解码失败，可能原文件不是UTF-8格式，则保持原样
        pass
    
    # 返回文件，明确指定UTF-8字符集
    response = HttpResponse(file_content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
    return response
