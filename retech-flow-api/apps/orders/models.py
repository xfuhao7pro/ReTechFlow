from django.db import models
from django.contrib.auth import get_user_model
from apps.goods.models import Goods
from .utils.snowflake import id_worker
User = get_user_model()

def generate_order_id():
    """
    动态生成雪花 ID 并转成字符串
    """
    return str(id_worker.get_id())

class Order(models.Model):
    """
    二手商品交易订单表
    """
    # 状态机枚举
    STATUS_CHOICES = (
        (0, '待付款'),
        (1, '待发货'),
        (2, '待收货'),
        (3, '交易成功'),
        (4, '交易取消'),
        (5, '售后/退款中'),
    )


    order_id = models.CharField(
        "订单号",
        max_length=50,
        unique=True,
        editable=False,
        default=generate_order_id
    )
    buyer = models.ForeignKey(User, related_name='buy_orders', on_delete=models.PROTECT, verbose_name="买家")
    seller = models.ForeignKey(User, related_name='sell_orders', on_delete=models.PROTECT, verbose_name="卖家")
    goods = models.ForeignKey(Goods, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="交易商品")
    amount = models.DecimalField("订单金额", max_digits=10, decimal_places=2)
    status = models.SmallIntegerField("订单状态", choices=STATUS_CHOICES, default=0)

    snapshot_content = models.TextField("商品文案快照", default="")
    snapshot_image = models.CharField("商品主图快照", max_length=255, default="")

    receiver_name = models.CharField("收货人姓名", max_length=20)
    receiver_phone = models.CharField("收货人电话", max_length=11)
    receiver_address = models.CharField("收货详细地址", max_length=200)
    tracking_number = models.CharField("快递单号", max_length=50, blank=True, null=True)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    pay_time = models.DateTimeField("付款时间", blank=True, null=True)
    consign_time = models.DateTimeField("发货时间", blank=True, null=True)
    finish_time = models.DateTimeField("成交时间", blank=True, null=True)

    class Meta:
        db_table = 'second_hand_order'
        verbose_name = "交易订单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"订单号: {self.order_id}"


