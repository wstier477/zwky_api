from django.apps import AppConfig
import sys
from django.conf import settings


class FaceRecognitionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'face_recognition'
    
    def ready(self):
        # 避免在管理命令中运行
        if 'runserver' not in sys.argv and 'uwsgi' not in sys.argv and 'gunicorn' not in sys.argv:
            return
            
        # 初始化人脸分析器
        from insightface.app import FaceAnalysis
        
        # 从settings获取配置
        face_config = getattr(settings, 'FACE_RECOGNITION', {})
        model_name = face_config.get('MODEL_NAME', 'buffalo_sc')
        providers = face_config.get('PROVIDERS', ['CUDAExecutionProvider', 'CPUExecutionProvider'])
        cuda_device_id = face_config.get('CUDA_DEVICE_ID', 0)
        det_size = face_config.get('DET_SIZE', (640, 640))
        
        # 创建全局变量
        self.face_analyzer = FaceAnalysis(name=model_name, providers=providers)
        self.face_analyzer.prepare(ctx_id=cuda_device_id, det_size=det_size)
        
        # 将分析器添加到模块全局变量中
        import face_recognition.views
        face_recognition.views.app = self.face_analyzer
