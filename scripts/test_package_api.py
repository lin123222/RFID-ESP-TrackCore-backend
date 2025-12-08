#!/usr/bin/env python3
"""
包裹API完整测试脚本
测试包括：用户认证、设备认证、包裹绑定、数据上传、数据查询、权限控制
"""

import requests
import json
import time
import hmac
import hashlib
from datetime import datetime
from loguru import logger

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

# 测试数据
TEST_USERNAME = "testuser_package"
TEST_PASSWORD = "test123456"
TEST_DEVICE_ID = "ESP32-TEST-001"
TEST_PACKAGE_ID = 2001


def build_signature_data(package_id, max_temperature, avg_humidity, over_threshold_time, timestamp):
    """构建签名字符串"""
    return (
        f"package_id={package_id}&"
        f"max_temperature={max_temperature:.2f}&"
        f"avg_humidity={avg_humidity:.2f}&"
        f"over_threshold_time={over_threshold_time}&"
        f"timestamp={timestamp}"
    )


def generate_hmac_signature(data, secret_key):
    """生成HMAC-SHA256签名"""
    return hmac.new(
        secret_key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def test_health():
    """测试健康检查接口"""
    logger.info("=" * 60)
    logger.info("1. 测试健康检查接口")
    logger.info("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return False


def test_user_register():
    """测试用户注册"""
    logger.info("\n" + "=" * 60)
    logger.info("2. 测试用户注册")
    logger.info("=" * 60)
    
    user_data = {
        "username": TEST_USERNAME,
        "email": f"{TEST_USERNAME}@example.com",
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        logger.info(f"状态码: {response.status_code}")
        result = response.json()
        logger.info(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            logger.success("✓ 用户注册成功")
            return True
        elif response.status_code == 400 and "already exists" in str(result):
            logger.warning("⚠ 用户已存在，继续测试")
            return True
        else:
            logger.error("✗ 用户注册失败")
            return False
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        return False


def test_user_login():
    """测试用户登录"""
    logger.info("\n" + "=" * 60)
    logger.info("3. 测试用户登录")
    logger.info("=" * 60)
    
    login_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        logger.info(f"状态码: {response.status_code}")
        result = response.json()
        logger.info(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            token = result["data"]["token"]
            logger.success(f"✓ 登录成功，Token: {token[:50]}...")
            return token
        else:
            logger.error("✗ 登录失败")
            return None
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        return None


def test_register_device(token):
    """测试注册设备"""
    logger.info("\n" + "=" * 60)
    logger.info("4. 测试注册设备")
    logger.info("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    device_data = {
        "device_id": TEST_DEVICE_ID,
        "device_name": "测试设备",
        "description": "用于测试的设备"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/devices", json=device_data, headers=headers)
        logger.info(f"状态码: {response.status_code}")
        result = response.json()
        logger.info(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            secret_key = result.get("secret_key")
            if secret_key:
                logger.success(f"✓ 设备注册成功")
                logger.info(f"⚠ Secret Key (请保存): {secret_key}")
                return secret_key
            else:
                logger.warning("⚠ 设备已存在，需要从数据库获取secret_key")
                return None
        elif response.status_code == 400:
            logger.warning("⚠ 设备已存在，继续测试（需要手动获取secret_key）")
            return None
        else:
            logger.error("✗ 设备注册失败")
            return None
    except Exception as e:
        logger.error(f"设备注册失败: {e}")
        return None


def test_bind_package(token):
    """测试绑定包裹"""
    logger.info("\n" + "=" * 60)
    logger.info("5. 测试绑定包裹")
    logger.info("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    package_data = {
        "package_id": TEST_PACKAGE_ID,
        "package_name": "测试包裹",
        "description": "这是一个测试包裹"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/packages/bind", json=package_data, headers=headers)
        logger.info(f"状态码: {response.status_code}")
        result = response.json()
        logger.info(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            logger.success("✓ 包裹绑定成功")
            return True
        else:
            logger.error("✗ 包裹绑定失败")
            return False
    except Exception as e:
        logger.error(f"绑定包裹失败: {e}")
        return False


def test_upload_package_data(secret_key):
    """测试ESP32上传包裹数据"""
    logger.info("\n" + "=" * 60)
    logger.info("6. 测试ESP32上传包裹数据（设备认证）")
    logger.info("=" * 60)
    
    if not secret_key:
        logger.error("✗ 缺少secret_key，无法测试上传")
        logger.info("提示：如果设备已存在，需要从数据库获取secret_key")
        return False
    
    # 准备数据
    timestamp = int(time.time())
    payload = {
        "package_id": TEST_PACKAGE_ID,
        "max_temperature": 28.5,
        "avg_humidity": 65.2,
        "over_threshold_time": 3600,
        "timestamp": timestamp
    }
    
    # 构建签名字符串
    sign_data = build_signature_data(
        package_id=payload["package_id"],
        max_temperature=payload["max_temperature"],
        avg_humidity=payload["avg_humidity"],
        over_threshold_time=payload["over_threshold_time"],
        timestamp=payload["timestamp"]
    )
    
    # 生成签名
    signature = generate_hmac_signature(sign_data, secret_key)
    
    # 设置请求头
    headers = {
        "X-Device-ID": TEST_DEVICE_ID,
        "X-Signature": signature,
        "X-Timestamp": str(timestamp),
        "Content-Type": "application/json"
    }
    
    logger.info(f"请求头: {json.dumps({k: v[:50] + '...' if len(str(v)) > 50 else v for k, v in headers.items()}, indent=2)}")
    logger.info(f"请求体: {json.dumps(payload, indent=2)}")
    logger.info(f"签名字符串: {sign_data}")
    logger.info(f"签名: {signature}")
    
    try:
        response = requests.post(f"{BASE_URL}/upload", json=payload, headers=headers)
        logger.info(f"状态码: {response.status_code}")
        result = response.json()
        logger.info(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            logger.success("✓ 数据上传成功")
            return True
        else:
            logger.error("✗ 数据上传失败")
            return False
    except Exception as e:
        logger.error(f"数据上传失败: {e}")
        return False


def test_get_package_records(token, package_id, should_succeed=True):
    """测试获取包裹记录"""
    logger.info("\n" + "=" * 60)
    logger.info(f"7. 测试获取包裹 {package_id} 的记录")
    logger.info("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "limit": 10,
        "offset": 0
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/packages/{package_id}/records",
            headers=headers,
            params=params
        )
        logger.info(f"状态码: {response.status_code}")
        result = response.json()
        logger.info(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if should_succeed:
            if response.status_code == 200:
                logger.success("✓ 查询成功")
                if "records" in result:
                    logger.info(f"  找到 {len(result['records'])} 条记录")
                return True
            else:
                logger.error("✗ 查询失败")
                return False
        else:
            if response.status_code == 403:
                logger.success("✓ 权限控制正常（正确拒绝了未授权的访问）")
                return True
            else:
                logger.error("✗ 权限控制异常（应该返回403）")
                return False
    except Exception as e:
        logger.error(f"查询失败: {e}")
        return False


def test_permission_control(token):
    """测试权限控制（尝试访问未绑定的包裹）"""
    logger.info("\n" + "=" * 60)
    logger.info("8. 测试权限控制（访问未绑定的包裹）")
    logger.info("=" * 60)
    
    # 尝试访问一个未绑定的包裹
    unauthorized_package_id = 9999
    return test_get_package_records(token, unauthorized_package_id, should_succeed=False)


def main():
    """主测试函数"""
    logger.info("\n" + "=" * 80)
    logger.info("包裹API完整测试")
    logger.info("=" * 80)
    
    results = {}
    
    # 1. 健康检查
    results["health"] = test_health()
    if not results["health"]:
        logger.error("服务器未运行，请先启动服务器")
        return
    
    # 2. 用户注册
    results["register"] = test_user_register()
    
    # 3. 用户登录
    token = test_user_login()
    if not token:
        logger.error("登录失败，无法继续测试")
        return
    results["login"] = True
    
    # 4. 注册设备
    secret_key = test_register_device(token)
    results["device"] = secret_key is not None
    
    # 5. 绑定包裹
    results["bind"] = test_bind_package(token)
    
    # 6. 上传数据（如果有secret_key）
    if secret_key:
        results["upload"] = test_upload_package_data(secret_key)
    else:
        logger.warning("跳过上传测试（缺少secret_key）")
        results["upload"] = None
    
    # 7. 查询包裹记录（已绑定）
    results["query"] = test_get_package_records(token, TEST_PACKAGE_ID, should_succeed=True)
    
    # 8. 权限控制测试
    results["permission"] = test_permission_control(token)
    
    # 测试总结
    logger.info("\n" + "=" * 80)
    logger.info("测试总结")
    logger.info("=" * 80)
    
    for test_name, result in results.items():
        if result is True:
            logger.success(f"✓ {test_name}: 通过")
        elif result is False:
            logger.error(f"✗ {test_name}: 失败")
        else:
            logger.warning(f"⚠ {test_name}: 跳过")
    
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    
    logger.info(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        logger.success("🎉 所有测试通过！")
    else:
        logger.warning("⚠ 部分测试失败，请检查日志")


if __name__ == "__main__":
    main()

