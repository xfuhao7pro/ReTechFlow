import random

def generate_default_nickname():
    """
    生成随机昵称
    """
    return f"用户_{random.randint(100000, 999999)}"