import requests
import json
import hashlib
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class KuaiDi100:
    def __init__(self):
        # settings 中读取配置
        self.customer = getattr(settings, 'KUAIDI100_CUSTOMER', None)
        self.key = getattr(settings, 'KUAIDI100_KEY', None)
        self.url = "https://poll.kuaidi100.com/poll/query.do"

    def get_track(self, tracking_num, com='auto'):
        """
        获取物流轨迹
        """
        if not self.customer or not self.key:
            return {'success': False, 'msg': "未配置 KUAIDI100_CUSTOMER 或 KUAIDI100_KEY"}

        param = {
            'com': com,
            'num': tracking_num,
            'resultv2': '1',
            'order': 'desc'
        }

        param_str = json.dumps(param)

        # 签名逻辑：MD5(param + key + customer)
        sign_str = param_str + self.key + self.customer
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()

        post_data = {
            'customer': self.customer,
            'param': param_str,
            'sign': sign
        }

        try:
            # 增加5秒超时保护
            response = requests.post(self.url, data=post_data, timeout=5)
            result = response.json()

            # 状态 200 表示查询成功
            if result.get('status') == '200':
                return {
                    'success': True,
                    'company': result.get('com'),
                    'data': result.get('data')
                }
            return {'success': False, 'msg': result.get('message', '查询失败')}
        except Exception:
            logger.exception("KuaiDi100 request failed")
            return {'success': False, 'msg': "物流接口暂时不可用，请稍后重试"}


# 导出单例
logistics_tool = KuaiDi100()
