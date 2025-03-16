from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .serializers import UserRegisterSerializer, UserLoginSerializer, UserInfoSerializer
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
