#!/usr/bin/env python
import os
import django

# 设置环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zwky_api.settings')
django.setup()

from django.contrib.auth import get_user_model
from course_management.models import Course, CourseTime
from user_management.models import Teacher, Student, User
from django.utils import timezone
import datetime

User = get_user_model()

def create_test_data():
    print("开始创建测试数据...")
    
    # 1. 创建测试教师用户
    teacher_user, created = User.objects.get_or_create(
        username="testteacher",
        defaults={
            "email": "testteacher@example.com",
            "role": "teacher",
        }
    )
    
    if created:
        teacher_user.set_password("Test@123456")
        teacher_user.save()
        print(f"创建教师用户: {teacher_user.username}")
    else:
        print(f"教师用户已存在: {teacher_user.username}")
    
    # 确保教师有教师个人资料
    teacher_profile, teacher_created = Teacher.objects.get_or_create(
        user=teacher_user,
        defaults={
            "teacher_title": "副教授",
        }
    )
    
    if teacher_created:
        print(f"创建教师个人资料，ID: {teacher_profile.teacher_id}")
    else:
        print(f"教师个人资料已存在，ID: {teacher_profile.teacher_id}")
    
    # 2. 创建测试学生用户 - 查找之前创建的testuser
    try:
        student_user = User.objects.get(username="testuser")
        print(f"找到学生用户: {student_user.username}")
        
        # 确保学生有学生个人资料
        student_profile, student_created = Student.objects.get_or_create(
            user=student_user
        )
        
        if student_created:
            print(f"创建学生个人资料，ID: {student_profile.student_id}")
        else:
            print(f"学生个人资料已存在，ID: {student_profile.student_id}")
    except User.DoesNotExist:
        print("未找到测试学生用户")
        return
    
    # 3. 创建测试课程
    course, course_created = Course.objects.get_or_create(
        title="测试课程",
        defaults={
            "description": "这是一个用于API测试的课程",
            "location": "教学楼 A101",
            "system": "必修",
            "schedule": "周一3-4节",
            "semester": "2025春季",
            "teacher": teacher_profile,
        }
    )
    
    if course_created:
        print(f"创建课程: {course.title}, ID: {course.course_id}")
    else:
        print(f"课程已存在: {course.title}, ID: {course.course_id}")
    
    # 4. 创建课程时间
    now = timezone.now()
    
    # 第一节课时间
    course_time1, ct1_created = CourseTime.objects.get_or_create(
        course=course,
        begin_time=now,
        defaults={
            "end_time": now + datetime.timedelta(hours=2),
            "teacher": teacher_profile,
        }
    )
    
    if ct1_created:
        print(f"创建课程时间 1: {course_time1}")
    else:
        print(f"课程时间 1 已存在: {course_time1}")
    
    # 第二节课时间
    next_week = now + datetime.timedelta(days=7)
    course_time2, ct2_created = CourseTime.objects.get_or_create(
        course=course,
        begin_time=next_week,
        defaults={
            "end_time": next_week + datetime.timedelta(hours=2),
            "teacher": teacher_profile,
        }
    )
    
    if ct2_created:
        print(f"创建课程时间 2: {course_time2}")
    else:
        print(f"课程时间 2 已存在: {course_time2}")
    
    # 5. 将学生加入课程
    from course_management.models import StudentCourse
    student_course, sc_created = StudentCourse.objects.get_or_create(
        student=student_profile,
        course=course
    )
    
    if sc_created:
        print(f"学生 {student_user.username} 已加入课程 {course.title}")
    else:
        print(f"学生 {student_user.username} 已在课程 {course.title} 中")
    
    print("测试数据创建完成！")

if __name__ == "__main__":
    create_test_data() 