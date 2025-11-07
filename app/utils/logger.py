"""
日志工具模块
提供统一的日志记录功能
"""
import logging
import sys
from datetime import datetime
from typing import Any

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("ispeake-api")


def log_info(message: str, **kwargs):
    """记录信息日志"""
    extra = f" - {kwargs}" if kwargs else ""
    logger.info(f"{message}{extra}")


def log_error(message: str, error: Exception = None, **kwargs):
    """记录错误日志"""
    extra = f" - {kwargs}" if kwargs else ""
    if error:
        logger.error(f"{message}: {type(error).__name__}: {error}{extra}", exc_info=True)
    else:
        logger.error(f"{message}{extra}")


def log_warning(message: str, **kwargs):
    """记录警告日志"""
    extra = f" - {kwargs}" if kwargs else ""
    logger.warning(f"{message}{extra}")


def log_debug(message: str, **kwargs):
    """记录调试日志"""
    extra = f" - {kwargs}" if kwargs else ""
    logger.debug(f"{message}{extra}")


def log_request(endpoint: str, method: str, user: str = "anonymous"):
    """记录API请求"""
    log_info(f"API请求: {method} {endpoint}", user=user)


def log_response(endpoint: str, status_code: int, duration_ms: float = None):
    """记录API响应"""
    duration = f" - 耗时: {duration_ms}ms" if duration_ms else ""
    log_info(f"API响应: {endpoint} - 状态码: {status_code}{duration}")

