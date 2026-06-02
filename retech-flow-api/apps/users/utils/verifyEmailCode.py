from django.core.cache import cache
def verify_email_code(email: str, auth_code: str) -> tuple[bool, str]:
    """
    校验邮箱验证码
    """

    cache_key = f'email_code:register:{email}'
    error_key = f'email_code_error:{email}'

    # 检查错误次数
    error_count = int(cache.get(error_key) or 0)
    if error_count >= 5:
        return False, '验证码错误次数过多，请重新获取'

    # 取出正确验证码
    real_code = cache.get(cache_key)
    if not real_code:
        return False, '验证码已过期，请重新获取'

    # 验证码错误
    if auth_code != str(real_code):
        cache.set(error_key, error_count + 1, timeout=600)
        return False, f'验证码错误，还可尝试 {4 - error_count} 次'

    # 验证通过，清除验证码和错误记录
    cache.delete(cache_key)
    cache.delete(error_key)
    return True, '验证通过'