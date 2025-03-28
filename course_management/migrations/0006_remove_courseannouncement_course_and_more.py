# Generated by Django 5.1.7 on 2025-03-25 15:07

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "course_management",
            "0005_alter_classcourse_options_alter_course_options_and_more",
        ),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="courseannouncement",
            name="course",
        ),
        migrations.RemoveField(
            model_name="courseannouncement",
            name="created_by",
        ),
        migrations.AlterModelOptions(
            name="classcourse",
            options={},
        ),
        migrations.AlterModelOptions(
            name="course",
            options={},
        ),
        migrations.AlterModelOptions(
            name="studentcourse",
            options={},
        ),
        migrations.CreateModel(
            name="CourseResource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="资源名称")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("document", "文档"),
                            ("image", "图片"),
                            ("video", "视频"),
                            ("other", "其他"),
                        ],
                        default="document",
                        max_length=20,
                        verbose_name="资源类型",
                    ),
                ),
                (
                    "size",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="文件大小"
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to="course_resources/%Y/%m/", verbose_name="资源文件"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="资源描述"),
                ),
                (
                    "upload_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="上传时间"
                    ),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "download_count",
                    models.IntegerField(default=0, verbose_name="下载次数"),
                ),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resources",
                        to="course_management.course",
                    ),
                ),
                (
                    "uploader",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="uploaded_resources",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "课程资源",
                "verbose_name_plural": "课程资源",
                "ordering": ["-upload_time"],
            },
        ),
        migrations.DeleteModel(
            name="Assignment",
        ),
        migrations.DeleteModel(
            name="CourseAnnouncement",
        ),
    ]
