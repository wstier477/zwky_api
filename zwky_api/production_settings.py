from zwky_api.settings import *

# 关闭调试模式
DEBUG = False

# 允许的主机
ALLOWED_HOSTS = ['您的服务器IP', '您的域名'] 

# 静态文件配置
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 媒体文件配置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 安全设置
SECURE_SSL_REDIRECT = False  # 如果使用HTTPS，设为True
SESSION_COOKIE_SECURE = False  # 如果使用HTTPS，设为True
CSRF_COOKIE_SECURE = False  # 如果使用HTTPS，设为True

# 数据库配置（如果需要使用MySQL或PostgreSQL）
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'zwky_db',
#         'USER': 'your_db_user',
#         'PASSWORD': 'your_db_password',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }

# CORS设置
CORS_ALLOW_ALL_ORIGINS = True 