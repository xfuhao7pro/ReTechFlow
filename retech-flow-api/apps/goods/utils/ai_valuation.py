import base64
import json
import logging
import os
import re
from io import BytesIO
from PIL import Image
from zhipuai import ZhipuAI
from django.conf import settings

logger = logging.getLogger(__name__)

API_KEY = settings.ZHIPUAI_API_KEY
client = ZhipuAI(api_key=API_KEY)

def image_to_base64(image_path):
    """
    压缩图片质量，更快响应大模型速度，提高用户体验
    避免大体积图片
    :param image_path:
    :return: Base64
    """
    with Image.open(image_path) as img:
        # 缩小尺寸
        img.thumbnail((800, 800))
        # 统一转成RGB格式防止PNG透明通道报错
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        buffered = BytesIO()
        # 压缩质量到80%
        img.save(buffered, format="JPEG", quality=80)
        # 转码返回
        return base64.b64encode(buffered.getvalue()).decode('utf-8')


def is_3c_product_by_llm(image_paths):
    """
    估价接口前置风控，判断用户是否上传的与3c数码产品无关
    """
    if not API_KEY:
        raise ValueError("AI 服务未配置 ZHIPUAI_API_KEY，请先检查后端环境变量。")

    try:
        message_content = []

        for i, path in enumerate(image_paths):
            base64_img = image_to_base64(path)
            message_content.append({"type": "text", "text": f"这是第 {i + 1} 张图片："})
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
            })

        prompt = f"你是一个安检程序。请务必逐一查看上面的 {len(image_paths)} 张图片！只要其中有任意一张包含手机、电脑、耳机、相机等数码产品，请仅输出一个字母 Y。只有当所有图片全都是非数码产品时，才输出 N。绝对不要输出任何标点符号、换行或其他废话。"
        message_content.append({"type": "text", "text": prompt})

        response = client.chat.completions.create(
            model="glm-4.6v",
            messages=[{"role": "user", "content": message_content}],
            temperature=0.1,
        )

        raw_content = response.choices[0].message.content
        result = raw_content.strip().upper()
        logger.info("AI safety check completed")

        return "Y" in result

    except Exception:
         logger.exception("AI safety check failed")
    raise ValueError("AI安检系统开小差了，请稍后再试!")


def evaluate_3c_goods(user_desc, image_paths=None):
    """
    if not API_KEY:
        raise ValueError("AI 服务未配置 ZHIPUAI_API_KEY，请先检查后端环境变量。")

    核心估价接口，详细的prompt要求
    :param user_desc:
    :param image_paths:
    :return:json格式响应
    """
    logger.info("Requesting AI valuation")

    system_prompt = """
    # Role
    你是一个二手电商平台的拥有极强网感的闲鱼资深卖家”。
    以图片中的数码产品为主，用户描述为辅完成需求：
    1. 真实二手估价：二手市场折旧率极高！请结合当前市场实际行情，给出真实的“二手回收底价”和“个人卖家成交价”，绝不能给出虚高的新机价格也不能低于大数据很多钱！
    2. 灵动标题：使用极具吸引力的“闲鱼风格/小红书风格”标题
    3. 爆款文案：
       - 拒绝幻觉：用户没提的就绝对不要写！可以着重渲染该型号的性能优势和用户的成色。
       - 排版要求：尽可能多的去描述字数至少150-250字左右，极力激发买家的购买欲和捡漏心理。
       - 型号要求: 详细介绍图片内的数码产品的类别，品牌，型号、芯片、颜色、内存等基础参数，吸引买家购买。
        所有商品都必须包含类似：“包邮发货，价格可聊，喜欢直接拍。二手商品一经售出不退不换，有问题随时私信！”的话术。
    # Output Schema
    严格输出以下 JSON，不要任何多余字符（title和description绝对不能重复）：
    {
        "title": "<string>",
        "description": "<string>",
        "min_price": <integer>,
        "max_price": <integer>
    }
    """
    structured_info = (
        f"用户的补充描述: {user_desc}\n\n"
        "警告：请直接返回包含 title, description, min_price, max_price 四个字段的纯 JSON 对象！"
    )
    message_content = [{"type": "text", "text": structured_info}]

    if image_paths:
        for path in image_paths:
            if os.path.exists(path):
                base64_img = image_to_base64(path)
                message_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}
                })

    try:
        response = client.chat.completions.create(
            model="glm-4.6v",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message_content}
            ],
            temperature=0.3,
        )

        result_text = response.choices[0].message.content.strip()

        json_match = re.search(r'\{[\s\S]*\}', result_text)
        if not json_match:
            logger.warning("AI valuation response did not contain a JSON object")
            return None

        json_str = json_match.group(0)

        try:
            return json.loads(json_str, strict=False)
        except Exception:
            logger.exception("Failed to parse AI valuation JSON")
            return None

    except Exception:
        logger.exception("AI valuation request failed")
        return None
