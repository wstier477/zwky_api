from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'role', 'name')
        extra_kwargs = {
            'name': {'source': 'first_name', 'required': True},
        }
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("邮箱已存在")
        return value
    
    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=first_name,
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    """用户登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class UserInfoSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    name = serializers.CharField(source='first_name')
    userId = serializers.CharField(source='id')
    createTime = serializers.DateTimeField(source='create_time', format='%Y-%m-%d %H:%M:%S')
    
    class Meta:
        model = User
        fields = ('userId', 'username', 'name', 'email', 'phone', 'role', 'avatar', 'createTime')
        read_only_fields = ('userId', 'username', 'createTime') 