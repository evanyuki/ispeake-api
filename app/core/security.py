"""
安全相关：JWT、密码加密
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
import hashlib
import bcrypt

from app.core.config import settings

# 密码加密上下文（bcrypt，与NestJS兼容）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    加密密码
    
    Args:
        password: 原始密码
    
    Returns:
        bcrypt加密后的密码哈希
    """
    # 先使用SHA256预处理，避免bcrypt 72字节限制
    preprocessed = _preprocess_password(password)
    return pwd_context.hash(preprocessed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """旧格式验证（模拟 NestJS 的 bcrypt.compareSync）"""
    try:
        # 直接使用 bcrypt.checkpw
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"  旧格式验证异常: {e}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT Token
    
    Args:
        data: 要编码的数据，通常包含 userId 和 userName
        expires_delta: 过期时间增量
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码JWT Token
    
    Returns:
        解码后的payload，包含 userId 和 userName
        失败返回 None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str) -> Dict[str, Any]:
    """
    验证Token并返回payload
    
    Raises:
        HTTPException: Token无效时抛出401错误
    """
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

