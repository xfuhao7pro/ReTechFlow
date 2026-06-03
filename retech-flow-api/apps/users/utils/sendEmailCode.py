import logging
import random
import threading

from django.core.cache import cache
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send_email_code_message(email: str, code: str, limit_key: str) -> None:
    try:
        send_mail(
            subject="欢迎使用3C二手智能估价交易平台",
            message=f"您的验证码是：{code}\n\n验证码5分钟内有效，请勿泄露给他人。",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.exception("Email verification code send failed: %s", exc)
        cache.delete(f"email_code:register:{email}")
        cache.delete(limit_key)


def get_code_cooldown(email: str) -> int:
    limit_key = f"email_code_limit:{email}"
    ttl = cache.ttl(limit_key) if hasattr(cache, "ttl") else None
    if isinstance(ttl, int) and ttl > 0:
        return ttl
    return 60


def send_email_code(email: str) -> tuple[bool, str, int]:
    """发送邮箱验证码，返回发送结果、提示文案和剩余冷却秒数。"""
    limit_key = f"email_code_limit:{email}"
    if cache.get(limit_key):
        return False, "发送太频繁，请稍后再试", get_code_cooldown(email)

    code = str(random.randint(100000, 999999))
    cache.set(f"email_code:register:{email}", code, timeout=300)
    cache.set(limit_key, 1, timeout=60)

    threading.Thread(
        target=_send_email_code_message,
        args=(email, code, limit_key),
        daemon=True,
    ).start()

    return True, "验证码已发送，请查收邮件", 60
