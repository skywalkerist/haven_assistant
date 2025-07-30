#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装依赖脚本 - 为不同环境安装必要的Python包
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行shell命令"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        return False

def install_base_dependencies():
    """安装base环境依赖"""
    print("📦 安装base环境依赖...")
    
    dependencies = [
        "flask",
        "requests", 
        "openai",
        "numpy"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"安装 {dep}"):
            return False
    
    return True

def install_face_dependencies():
    """安装face环境依赖"""
    print("📦 安装face环境依赖...")
    
    face_env_pip = "/home/xuanwu/miniconda/envs/face/bin/pip"
    
    if not os.path.exists(face_env_pip):
        print(f"❌ face环境pip未找到: {face_env_pip}")
        return False
    
    dependencies = [
        "flask",
        "requests"
    ]
    
    for dep in dependencies:
        if not run_command(f"{face_env_pip} install {dep}", f"在face环境安装 {dep}"):
            return False
    
    return True

def check_existing_packages():
    """检查现有包"""
    print("🔍 检查现有包...")
    
    # 检查base环境
    print("Base环境包:")
    subprocess.run("pip list | grep -E '(flask|requests|openai)'", shell=True)
    
    # 检查face环境
    print("\nFace环境包:")
    face_env_pip = "/home/xuanwu/miniconda/envs/face/bin/pip"
    if os.path.exists(face_env_pip):
        subprocess.run(f"{face_env_pip} list | grep -E '(flask|requests|insightface)'", shell=True)

def main():
    """主函数"""
    print("=" * 60)
    print("🛠️  超级智能体依赖安装")
    print("=" * 60)
    
    print("📋 将安装以下依赖:")
    print("• Base环境: flask, requests, openai, numpy")
    print("• Face环境: flask, requests")
    
    response = input("\n是否继续安装? (y/n): ").strip().lower()
    if response != 'y':
        print("安装已取消")
        return
    
    # 安装base环境依赖
    if not install_base_dependencies():
        print("❌ base环境依赖安装失败")
        return
    
    # 安装face环境依赖
    if not install_face_dependencies():
        print("❌ face环境依赖安装失败")
        return
    
    print("\n✅ 所有依赖安装完成!")
    print("\n📊 安装后的包列表:")
    check_existing_packages()

if __name__ == "__main__":
    main()