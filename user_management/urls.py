from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, LoginView, LogoutView
from .views import UserMessageView, UserProfileView

urlpatterns = [
    # 认证相关
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 用户消息相关
    path('user/messages/', UserMessageView.as_view(), name='user_messages'),
    # 用户资料相关
    path('users/profile/', UserProfileView.as_view(), name='user_profile'),
]