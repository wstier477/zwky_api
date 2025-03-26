from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserInfoSerializer, UserMessageSerializer
from .utils import api_response, ErrorCode

User = get_user_model()

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
                refresh = RefreshToken.for_user(user)
                user_data = UserInfoSerializer(user).data
                
                return api_response(
                    code=200,
                    message="登录成功",
                    data={
                        "token": str(refresh.access_token),
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
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取当前登录用户的所有消息"""
        user = request.user
        serializer = UserMessageSerializer(user)
        
        return api_response(
            code=200,
            message="获取用户消息成功",
            data=serializer.data
        )
    
    def post(self, request):
        """根据用户ID获取指定用户的所有消息"""
        try:
            user_id = request.data.get('user_id')
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