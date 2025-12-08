#!/usr/bin/env python3
"""
API测试脚本
"""

import requests
import json
from loguru import logger

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """测试健康检查接口"""
    logger.info("测试健康检查接口...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return False


def test_user_registration():
    """测试用户注册"""
    logger.info("测试用户注册...")
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        return False


def test_user_login():
    """测试用户登录"""
    logger.info("测试用户登录...")
    
    login_data = {
        "username": "admin",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        logger.info(f"状态码: {response.status_code}")
        result = response.json()
        logger.info(f"响应: {result}")
        
        if response.status_code == 200:
            token = result["data"]["token"]
            logger.success(f"登录成功，获得Token: {token[:50]}...")
            return token
        return None
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        return None


def test_get_user_info(token):
    """测试获取用户信息"""
    logger.info("测试获取用户信息...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        return False


def test_bind_package(token):
    """测试绑定包裹"""
    logger.info("测试绑定包裹...")
    
    headers = {"Authorization": f"Bearer {token}"}
    package_data = {
        "package_id": 1001,
        "package_name": "测试包裹",
        "description": "这是一个测试包裹"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/packages/bind", json=package_data, headers=headers)
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"绑定包裹失败: {e}")
        return False


def test_get_packages(token):
    """测试获取包裹列表"""
    logger.info("测试获取包裹列表...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/packages", headers=headers)
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"获取包裹列表失败: {e}")
        return False


def test_get_package_records(token, package_id=1001):
    """测试获取包裹记录"""
    logger.info(f"测试获取包裹 {package_id} 的记录...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/monitor/{package_id}/records", headers=headers)
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"获取包裹记录失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("=== API 测试开始 ===")
    
    # 测试健康检查
    if not test_health():
        logger.error("健康检查失败，请确保服务器正在运行")
        return
    
    # 测试用户注册（可能失败，如果用户已存在）
    test_user_registration()
    
    # 测试用户登录
    token = test_user_login()
    if not token:
        logger.error("登录失败，无法继续测试")
        return
    
    # 测试获取用户信息
    test_get_user_info(token)
    
    # 测试绑定包裹
    test_bind_package(token)
    
    # 测试获取包裹列表
    test_get_packages(token)
    
    # 测试获取包裹记录
    test_get_package_records(token)
    
    logger.success("=== API 测试完成 ===")


if __name__ == "__main__":
    main()
