import random
from django.core.mail import send_mail
from django.core.cache import cache


def send_email_code(email: str) -> tuple[bool, str]:
    """
    发送邮箱验证码
    :return
    """
    # 60秒冷却防刷
    limit_key = f'email_code_limit:{email}'
    if cache.get(limit_key):
        return False, '发送太频繁，请60秒后再试'

    # 生成6位验证码
    code = str(random.randint(100000, 999999))
    # 存入 Redis
    cache.set(f'email_code:register:{email}', code, timeout=300)
    cache.set(limit_key, 1, timeout=60)

    # 发送邮件
    try:
        send_mail(
            subject='欢迎使用3C二手智能估价交易平台！',
            message=f'您的注册验证码是：{code}\n\n验证码5分钟内有效，请勿泄露给他人。',
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        cache.delete(f'email_code:register:{email}')
        cache.delete(limit_key)
        return False, '邮件发送失败，请稍后重试'

    return True, '验证码已发送，请查收邮件'