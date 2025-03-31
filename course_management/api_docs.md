# 课程管理系统 API 文档

## 目录
1. [课程列表](#课程列表)
2. [课程详情](#课程详情)
3. [课程资源列表](#课程资源列表)
4. [资源详情](#资源详情)
5. [资源下载](#资源下载)
6. [课程学生信息](#课程学生信息)

## 课程列表

### 接口描述
获取当前用户相关的课程列表

### 请求信息
- 请求方法：GET
- 请求路径：/api/courses/
- 需要认证：是

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |

### 响应信息
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "total": 10,
        "items": [
            {
                // 课程信息
            }
        ]
    }
}
```

## 课程详情

### 接口描述
获取特定课程的详细信息

### 请求信息
- 请求方法：GET
- 请求路径：/api/courses/{course_id}/
- 需要认证：是

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | string | 是 | 课程ID |

### 响应信息
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        // 课程详细信息
    }
}
```

## 课程资源列表

### 接口描述
获取和上传课程资源

### 获取资源列表
#### 请求信息
- 请求方法：GET
- 请求路径：/api/courses/{course_id}/resources/
- 需要认证：是

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | string | 是 | 课程ID |
| type | string | 否 | 资源类型过滤 |
| search | string | 否 | 搜索关键词 |
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |

#### 响应信息
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "total": 10,
        "items": [
            {
                // 资源信息
            }
        ]
    }
}
```

### 上传资源
#### 请求信息
- 请求方法：POST
- 请求路径：/api/courses/{course_id}/resources/
- 需要认证：是
- Content-Type: multipart/form-data

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | string | 是 | 课程ID |
| file | file | 是 | 上传的文件 |
| name | string | 否 | 资源名称 |
| type | string | 否 | 资源类型 |
| description | string | 否 | 资源描述 |

#### 响应信息
```json
{
    "code": 200,
    "message": "上传成功",
    "data": {
        // 资源信息
    }
}
```

## 资源详情

### 获取资源详情
#### 请求信息
- 请求方法：GET
- 请求路径：/api/resources/{resource_id}/
- 需要认证：是

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| resource_id | string | 是 | 资源ID |

#### 响应信息
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        // 资源详细信息
    }
}
```

### 删除资源
#### 请求信息
- 请求方法：DELETE
- 请求路径：/api/resources/{resource_id}/
- 需要认证：是

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| resource_id | string | 是 | 资源ID |

#### 响应信息
```json
{
    "code": 200,
    "message": "删除成功",
    "data": null
}
```

## 资源下载

### 接口描述
下载课程资源

### 请求信息
- 请求方法：GET
- 请求路径：/api/resources/{resource_id}/download/
- 需要认证：是

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| resource_id | string | 是 | 资源ID |

### 响应信息
- 成功：直接返回文件流
- 失败：返回JSON格式错误信息
```json
{
    "code": 200,
    "message": "下载链接生成成功",
    "data": {
        "downloadUrl": "文件下载地址"
    }
}
```

## 课程学生信息

### 接口描述
获取课程学生的详细信息（仅教师可用）

### 请求信息
- 请求方法：GET
- 请求路径：/api/courses/{course_id}/students/
- 需要认证：是

### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| course_id | string | 是 | 课程ID |

### 响应信息
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "total": 10,
        "items": [
            {
                "student_id": "S000001",
                "email": "student@example.com",
                "phone": "1234567890",
                "staff_id": "ST001",
                "image": "头像URL",
                "class_name": "班级名称",
                "class_system": "班级系统"
            }
        ]
    }
}
```

### 错误码说明
| 错误码 | 描述 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 403 | 无权限访问 |
| 404 | 资源不存在 | 