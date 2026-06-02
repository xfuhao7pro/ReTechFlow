import re

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    校验密码强度
    :return: (是否通过, 提示信息)
    """
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[_\.@])[a-zA-Z\d_\.@]{6,20}$'
    if not re.match(pattern, password):
        return False, '密码长度为 6-20 位，需包含大小写字母、数字及特殊字符（_ . @）'
    return True, '密码格式正确'