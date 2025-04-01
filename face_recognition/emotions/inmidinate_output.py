from PIL import Image, ImageDraw, ImageFont
from dbmodule import *
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from emotions import *
# 检测人脸
app = FaceAnalysis(name="buffalo_sc", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

# 创建数据库连接
emotion=MultiFaceDetector()
data_collector=DataCollector()
logger=StatusLogger()

def process_frame(frame, target_feats, target_names,student_name,similarity_threshold=0.45):
    """
    处理视频帧，检测人脸并实时输出匹配结果。

    参数:
        frame (np.ndarray): 视频帧（单张图像）。
        target_feats (list): 目标人脸特征向量列表。
        target_names (list): 目标人脸名字列表。
        similarity_threshold (float): 相似度阈值，默认 0.6。

    返回:
        frame (np.ndarray): 绘制了人脸框和标签的视频帧。
        num_faces (int): 检测到的人脸数量。
        matched (bool): 是否在数据库中找到了匹配项。
    """

    # 如果 frame 为 None，直接返回原帧
    if frame is None:
        print("警告：frame 为 None")
        return frame, 0, False

    # 检测人脸
    faces = app.get(frame)
    if not faces:
        print("未检测到人脸")
        return frame, 0, False  # 如果没有检测到人脸，直接返回原帧

    # 输出检测到的人脸数量
    num_faces = len(faces)
    print(f"检测到 {num_faces} 张人脸")

    # 提取检测到的人脸特征向量
    feats = np.array([face.normed_embedding for face in faces], dtype=np.float32)

    # 初始化匹配标志
    matched = False

    # 将 OpenCV 图像转换为 PIL 图像
    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(frame_pil)

    # 加载中文字体
    font_path = "simsun.ttc"  # 替换为你的中文字体文件路径
    font = ImageFont.truetype(font_path, 12)  # 字体大小

    # 遍历所有检测到的人脸
    for i, face in enumerate(faces):
        # 获取人脸框坐标
        bbox = face.bbox.astype(np.int64)  # 人脸框坐标,这是归一化后的人脸坐标向量
        # 分析指定ROI内的人脸
        # 从bbox裁剪人脸区域
        x1, y1, x2, y2 = map(int, bbox)
        aframe = frame[y1:y2, x1:x2]
        aframe,status_emotions=emotion.process_frame(aframe)
        # 为每个人脸生成唯一ID (使用人脸位置作为临时ID)
        #face_id = f"{bbox[0]}_{bbox[1]}_{bbox[2]}_{bbox[3]}"



        # 初始化匹配信息
        match_found = False
        target_name = "unknown"
        max_similarity=0.45

        # 对比当前人脸与目标人脸特征向量
        for j, target_feat in enumerate(target_feats):
            sim = np.dot(feats[i], target_feat)  # 计算相似度
            if sim > max_similarity:
                max_similarity = sim
                if max_similarity > similarity_threshold:
                    match_found = True
                    target_name = target_names[j]
                    matched = True  # 标记为找到匹配项
        #检测到存在于数据库中的人脸，即阈值大于similarity_threshold的人脸
        if match_found:
            student_name.add(target_name)
        # 设置标签
        label = f"{target_name} ({max_similarity:.2f}) {status_emotions['main_status']}" if match_found else "unknown"
        status_data={
            'id':i,
            'name':target_name,
            'main_status': status_emotions['main_status']}
        #更新数据收集器
        data_collector.update_status(status_data)
        if status_data['name'] != 'unknown':
            #记录日志
            logger.log_status(status_data)
            # 绘制人脸框
            frame = app.draw_on(frame, [face])

        # 在人脸框上方添加名字和相似度
        draw.text(
            (bbox[0], bbox[1] - 40),  # 文字位置
            label,  # 名字和相似度
            font=font,  # 字体
            fill=(0, 255, 0) if match_found else (255, 0, 0)  # 颜色 (绿色匹配，红色未知)
        )

    # 将 PIL 图像转换回 OpenCV 图像
    frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

    # 输出是否找到匹配项
    if matched:
        print("在数据库中找到了匹配项")
    else:
        print("未在数据库中找到匹配项")

    return frame

def showFace(frame):
    # 检测人脸
    faces = app.get(frame)
    target_feats, target_names = load_target_feats_from_db(r"data/faces.db")
    aset=set()
    frame = process_frame(frame, target_feats, target_names,aset)
    # 遍历所有检测到的人脸
    for i, face in enumerate(faces):
        # 获取人脸框坐标
        bbox = face.bbox.astype(np.int64)  # 人脸框坐标

    # 绘制人脸框
        frame = app.draw_on(frame, [face])

    return frame

# 示例：实时处理视频流
if __name__ == '__main__':
    # 加载目标人脸特征向量
    #target_folder = r"data/targetFace"
    db_path = r"F:\AAC\AAAzwkyy\zwky_api\db.sqlite3"
    target_feats, target_names = load_target_feats_from_db(db_path)

    # 打开摄像头
    cap = cv2.VideoCapture(0)  # 0 表示默认摄像头
    if not cap.isOpened():
        print("无法打开摄像头")
        exit()

    while True:
        # 读取视频帧
        ret, frame = cap.read()
        if not ret:
            print("无法读取视频帧")
            break

        # 处理视频帧
        result_frame = showFace(frame)

        # 显示结果
        if result_frame is None or not isinstance(result_frame, np.ndarray):
            print("Error: result_frame is not a valid image.")
        else:
            cv2.imshow("Face Recognition", result_frame)

        # 按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()