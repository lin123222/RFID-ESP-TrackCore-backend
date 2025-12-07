"""
安全工具函数
用于 HMAC 签名验证、密钥生成等
"""
import hmac
import hashlib
import secrets
from typing import Optional


def generate_secret_key() -> str:
    """
    生成 32 字节的 Secret Key（64字符十六进制）
    
    Returns:
        64字符的十六进制字符串
    """
    return secrets.token_hex(32)


def build_signature_data(
    package_id: int,
    max_temperature: float,
    avg_humidity: float,
    over_threshold_time: int,
    timestamp: int
) -> str:
    """
    构建用于签名的数据字符串
    按照固定顺序拼接所有字段，确保签名一致性
    
    Args:
        package_id: 包裹ID
        max_temperature: 最高温度
        avg_humidity: 平均湿度
        over_threshold_time: 超阈值时间
        timestamp: 时间戳
        
    Returns:
        用于签名的数据字符串
    """
    # 按照固定格式拼接，确保顺序一致
    # 注意：浮点数需要格式化，避免精度问题
    return (
        f"package_id={package_id}&"
        f"max_temperature={max_temperature:.2f}&"
        f"avg_humidity={avg_humidity:.2f}&"
        f"over_threshold_time={over_threshold_time}&"
        f"timestamp={timestamp}"
    )


def generate_hmac_signature(data: str, secret_key: str) -> str:
    """
    生成 HMAC-SHA256 签名
    
    Args:
        data: 要签名的数据（通常是 JSON 字符串）
        secret_key: 密钥
        
    Returns:
        HMAC-SHA256 签名的十六进制字符串（64字符）
    """
    signature = hmac.new(
        secret_key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature


def verify_hmac_signature(
    data: str,
    signature: str,
    secret_key: str
) -> bool:
    """
    验证 HMAC-SHA256 签名
    
    使用安全的比较方法，防止时序攻击
    
    Args:
        data: 原始数据
        signature: 待验证的签名
        secret_key: 密钥
        
    Returns:
        验证是否通过
    """
    expected_signature = generate_hmac_signature(data, secret_key)
    
    # 使用安全的比较方法，防止时序攻击
    return hmac.compare_digest(expected_signature, signature)

