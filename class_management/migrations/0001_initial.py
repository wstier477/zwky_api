# Generated by Django 5.1.7 on 2025-03-20 10:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('class_id', models.AutoField(primary_key=True, serialize=False)),
                ('class_name', models.CharField(max_length=45)),
                ('class_system', models.CharField(max_length=45)),
            ],
        ),
        migrations.CreateModel(
            name='TeacherClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_classes', to='class_management.class')),
            ],
        ),
    ]
