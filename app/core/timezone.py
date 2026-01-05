"""
时区工具模块 - 统一使用北京时间 (UTC+8)
"""
from datetime import datetime, timezone, timedelta

# 北京时间 UTC+8
BEIJING_TZ = timezone(timedelta(hours=8))


def now_beijing() -> datetime:
    """获取当前北京时间"""
    return datetime.now(BEIJING_TZ)


def to_beijing(dt: datetime) -> datetime:
    """将时间转换为北京时间"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # 如果没有时区信息，假设是 UTC
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(BEIJING_TZ)


def format_beijing(dt: datetime) -> str:
    """格式化为北京时间的 ISO 格式字符串"""
    if dt is None:
        return None
    return to_beijing(dt).isoformat()
