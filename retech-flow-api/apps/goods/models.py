import shortuuid
from django.db import models
from django.conf import settings


def generate_short_uuid():
    return shortuuid.uuid()


# 商品状态
class GoodsStatusChoices(models.IntegerChoices):
    DRAFT = 0, "草稿"
    ON_SALE = 1, "在售中"
    SOLD = 2, "已售出"
    OFF_SHELVES = 3, "已下架"
# 发货方式
class DeliveryMethodChoices(models.IntegerChoices):
    FREE_SHIPPING = 1, "包邮"
    FREIGHT_COLLECT = 2, "到付"  # 3C产品写顺丰到付显得极专业
    SELF_PICKUP = 3, "自提"
# 商品分类
class Category(models.Model):
    """
    商品大类
    """
    name = models.CharField("分类名称", max_length=50, unique=True)
    sort = models.IntegerField("排序", default=0)

    class Meta:
        db_table = 'goods_category'
        verbose_name = "商品分类"
        verbose_name_plural = verbose_name
        ordering = ['sort']

    def __str__(self):
        return self.name

# 商品属性
class CategoryAttribute(models.Model):
    """
    分类专属属性
    """
    category = models.ForeignKey(Category, related_name='attributes', on_delete=models.CASCADE, verbose_name="所属大类")
    name = models.CharField("属性名", max_length=50)
    options = models.JSONField("备选项", default=list)

    class Meta:
        db_table = 'goods_category_attribute'
        verbose_name = "分类动态属性"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.category.name} - {self.name}"

# 二手商品表
class Goods(models.Model):
    id = models.CharField(primary_key=True, max_length=22, default=generate_short_uuid, editable=False)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="published_goods",
                               verbose_name="卖家")

    title = models.CharField("商品标题", max_length=100)
    description = models.TextField("商品详情")
    price = models.DecimalField("售价", max_digits=10, decimal_places=2)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="商品分类")

    attributes = models.JSONField("动态属性", default=dict, blank=True, null=True)

    delivery_method = models.IntegerField(
        "发货方式",
        choices=DeliveryMethodChoices.choices,
        default=DeliveryMethodChoices.FREE_SHIPPING
    )
    status = models.IntegerField("商品状态", choices=GoodsStatusChoices.choices,
                                 default=GoodsStatusChoices.ON_SALE)
    views = models.PositiveIntegerField("浏览量", default=0)

    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = 'second_hand_goods'
        ordering = ['-created_at']
        verbose_name = "商品信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

# 商品收藏表
class GoodsLike(models.Model):
    """
    商品收藏表
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='like', verbose_name='用户')
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name='like_by', verbose_name='商品')
    created_at = models.DateTimeField('收藏时间', auto_now_add=True)

    class Meta:
        db_table = 'goods_like'
        verbose_name = '商品收藏'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'goods')

# 商品图片表
class GoodsImage(models.Model):
    id = models.CharField(primary_key=True, max_length=22, default=generate_short_uuid, editable=False)
    goods = models.ForeignKey(Goods, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("商品图片", upload_to="goods/images/%Y/%m/")
    is_cover = models.BooleanField("是否为主图", default=False)
    created_at = models.DateTimeField("上传时间", auto_now_add=True)

    class Meta:
        db_table = 'second_hand_goods_image'
        ordering = ['-is_cover', 'created_at']

