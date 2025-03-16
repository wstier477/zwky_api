#!/usr/bin/env python
"""
部署前准备检查脚本
用于检查项目是否准备好部署到PythonAnywhere
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("警告: 推荐使用Python 3.8或更高版本。当前版本:", sys.version)
        return False
    print("Python版本检查通过:", sys.version)
    return True

def check_requirements():
    """检查依赖包是否已安装"""
    print("检查依赖包...")
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("错误: requirements.txt文件不存在")
        return False
    
    with open(requirements_file, "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    missing_packages = []
    for req in requirements:
        package_name = req.split("==")[0]
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            missing_packages.append(req)
    
    if missing_packages:
        print("警告: 以下依赖包未安装:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        return False
    
    print("依赖包检查通过")
    return True

def check_django_settings():
    """检查Django设置文件"""
    print("检查Django设置文件...")
    settings_file = Path("zwky_api/pythonanywhere_settings.py")
    if not settings_file.exists():
        print("错误: pythonanywhere_settings.py文件不存在")
        return False
    
    print("Django设置文件检查通过")
    return True

def check_wsgi_file():
    """检查WSGI文件"""
    print("检查WSGI文件...")
    wsgi_file = Path("pythonanywhere_wsgi.py")
    if not wsgi_file.exists():
        print("错误: pythonanywhere_wsgi.py文件不存在")
        return False
    
    print("WSGI文件检查通过")
    return True

def check_static_directory():
    """检查静态文件目录"""
    print("检查静态文件目录...")
    static_dir = Path("static")
    if not static_dir.exists():
        print("注意: static目录不存在，将在部署时创建")
    
    print("静态文件目录检查通过")
    return True

def check_deploy_script():
    """检查部署脚本"""
    print("检查部署脚本...")
    deploy_script = Path("deploy_to_pythonanywhere.sh")
    if not deploy_script.exists():
        print("错误: deploy_to_pythonanywhere.sh文件不存在")
        return False
    
    print("部署脚本检查通过")
    return True

def check_git_repo():
    """检查Git仓库状态"""
    print("检查Git仓库状态...")
    try:
        result = subprocess.run(
            ["git", "status"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        if result.returncode != 0:
            print("注意: 当前目录不是Git仓库，推荐使用Git进行版本控制")
            return True
        
        # 检查是否有未提交的更改
        if "nothing to commit" not in result.stdout:
            print("警告: 有未提交的更改，建议在部署前提交所有更改")
            return False
        
        print("Git仓库状态检查通过")
        return True
    except FileNotFoundError:
        print("注意: Git未安装或不在PATH中，跳过Git检查")
        return True

def main():
    """主函数"""
    print("开始部署前检查...\n")
    
    checks = [
        check_python_version,
        check_requirements,
        check_django_settings,
        check_wsgi_file,
        check_static_directory,
        check_deploy_script,
        check_git_repo
    ]
    
    results = [check() for check in checks]
    
    print("\n检查结果摘要:")
    if all(results):
        print("✅ 所有检查通过！项目已准备好部署到PythonAnywhere。")
    else:
        print("❌ 部分检查未通过。请修复上述问题后再尝试部署。")
    
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main()) 