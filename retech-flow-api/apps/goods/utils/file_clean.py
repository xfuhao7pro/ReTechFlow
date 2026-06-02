import os
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def clean_expired_temp_files(expiration_time=3600):
    """
    清理临时文件夹(media/temp)中过期的文件
    :param expiration_time: 过期时间（秒），默认 3600 秒（1小时）
    """
    # 确保路径是基于 Django 配置的 MEDIA_ROOT
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')

    if not os.path.exists(temp_dir):
        return

    now = time.time()

    try:
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            # 确保是文件而不是文件夹
            if os.path.isfile(file_path):
                # 获取文件的最后修改时间
                file_modify_time = os.stat(file_path).st_mtime
                # 如果存活时间超过了设定的时效
                if file_modify_time < now - expiration_time:
                    os.remove(file_path)
    except Exception:
        # 捕获异常，防止因为个别文件被占用导致整个进程崩溃
        logger.exception("Failed to clean expired temporary files")
