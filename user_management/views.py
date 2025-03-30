from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework import status
# from django.views.decorators.csrf import csrf_exempt  # 不再需要CSRF装饰器
# from django.utils.decorators import method_decorator  # 不再需要装饰器工具
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserInfoSerializer, UserMessageSerializer
from .utils import api_response, ErrorCode

User = get_user_model()

# 自定义令牌刷新视图
class CustomTokenRefreshView(TokenRefreshView):
    """
    自定义令牌刷新视图，格式化响应格式
    """
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = TokenRefreshSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return api_response(
                code=400,
                message="刷新令牌无效或已过期",
                data=None
            )
            
        return api_response(
            code=200,
            message="令牌刷新成功",
            data=serializer.validated_data
        )

class RegisterView(APIView):
    """
    用户注册视图
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_data = UserInfoSerializer(user).data
            return api_response(
                code=200,
                message="注册成功",
                data={
                    "userId": user_data['userId'],
                    "username": user_data['username']
                }
            )
        else:
            # 处理验证错误
            if 'username' in serializer.errors:
                return api_response(
                    code=ErrorCode.USERNAME_EXISTS,
                    message="用户名已存在",
                    data=None
                )
            elif 'email' in serializer.errors:
                return api_response(
                    code=ErrorCode.EMAIL_EXISTS,
                    message="邮箱已存在",
                    data=None
                )
            else:
                return api_response(
                    code=400,
                    message=str(serializer.errors),
                    data=None
                )


# 移除CSRF装饰器
class LoginView(APIView):
    """
    用户登录视图
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # 生成JWT令牌
                refresh = RefreshToken.for_user(user)
                user_data = UserInfoSerializer(user).data
                
                return api_response(
                    code=200,
                    message="登录成功",
                    data={
                        "token": str(refresh.access_token),  # 访问令牌
                        "refresh": str(refresh),             # 刷新令牌
                        "userId": user_data['userId'],
                        "username": user_data['username'],
                        "role": user_data['role'],
                        "avatar": user_data['avatar']
                    }
                )
            else:
                return api_response(
                    code=ErrorCode.INVALID_CREDENTIALS,
                    message="用户名或密码错误",
                    data=None
                )
        else:
            return api_response(
                code=400,
                message=str(serializer.errors),
                data=None
            )

class LogoutView(APIView):
    """
    用户退出登录视图
    """
    permission_classes = [AllowAny]  # 修改为允许任何人访问
    
    def post(self, request):
        # JWT无状态，客户端只需删除token即可
        return api_response(
            code=200,
            message="退出成功",
            data=None
        )

class UserMessageView(APIView):
    """
    用户消息视图
    获取用户的所有消息，包括关联的课程和课时状态等信息
    """
    # 用户消息接口需要认证
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取当前登录用户的所有消息"""
        # 优先使用已验证的登录用户
        if request.user.is_authenticated:
            user = request.user
        else:
            # 向下兼容，仍然支持通过参数获取
            user_id = request.query_params.get('user_id')
            if not user_id:
                return api_response(
                    code=400,
                    message="用户ID不能为空",
                    data=None
                )
                
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return api_response(
                    code=404,
                    message="用户不存在",
                    data=None
                )
                
        serializer = UserMessageSerializer(user)
        
        return api_response(
            code=200,
            message="获取用户消息成功",
            data=serializer.data
        )
    
    def post(self, request):
        """根据用户ID获取指定用户的所有消息"""
        try:
            # 优先使用请求中的用户ID
            user_id = request.data.get('user_id')
            
            # 如果没有用户ID且用户已登录，使用当前用户
            if not user_id and request.user.is_authenticated:
                user = request.user
            else:
                if not user_id:
                    return api_response(
                        code=400,
                        message="用户ID不能为空",
                        data=None
                    )
                    
                user = User.objects.get(id=user_id)
                
            serializer = UserMessageSerializer(user)
            
            return api_response(
                code=200,
                message="获取用户消息成功",
                data=serializer.data
            )
        except User.DoesNotExist:
            return api_response(
                code=404,
                message="用户不存在",
                data=None
            )
        except Exception as e:
            return api_response(
                code=500,
                message=f"服务器错误: {str(e)}",
                data=None
            )