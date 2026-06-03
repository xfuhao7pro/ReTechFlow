import os
from rest_framework import serializers
from django.core.files.storage import default_storage
from django.core.files import File
from .models import Goods, GoodsImage, Category,CategoryAttribute
from apps.users.serializers import UserProfileSerializer

# 属性序列化
class CategoryAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryAttribute
        fields = ['name', 'options']

# 类别序列化
class CategorySerializer(serializers.ModelSerializer):
    attributes = CategoryAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'sort', 'attributes']
# 图片序列化
class GoodsImageSerializer(serializers.ModelSerializer):
    """
    商品图片序列化
    """
    class Meta:
        model = GoodsImage
        fields = ['id', 'image', 'is_cover', 'created_at']

# 商品序列化
class GoodsSerializer(serializers.ModelSerializer):
    """
    商品序列化
    """
    title = serializers.CharField(max_length=100, required=False, allow_blank=True)
    description = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True,
        error_messages={"max_length": "老板，商品详情太长了，系统存不下啦！"}
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)

    category_id = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": "您选择的分类不存在哦！"}
    )

    attributes = serializers.JSONField(required=False, default=dict)

    temp_images = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False,
        default=list  # 没传图默认给空列表
    )
    is_like = serializers.SerializerMethodField()
    wants = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    images = GoodsImageSerializer(many=True, read_only=True)
    seller = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Goods
        fields = [
            'id', 'title', 'description', 'price',
            'category', 'category_id', 'attributes','delivery_method',
            'status', 'audit_reason', 'views', 'created_at', 'updated_at',
            'temp_images', 'images','is_like', 'wants', 'seller', 'cover'
        ]
        read_only_fields = ['id', 'views', 'created_at', 'updated_at']

    def get_cover(self, obj):
        """获取商品封面图"""
        cover_image = obj.images.filter(is_cover=True).first()
        if not cover_image:
            cover_image = obj.images.first()
        if cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(cover_image.image.url)
            return cover_image.image.url
        return None

    def get_wants(self, obj):
        """获取想要该商品的人数（收藏数）"""
        return obj.like_by.count()

    def get_is_like(self, obj):
        """动态计算当前请求的用户是否收藏了该商品"""
        request = self.context.get('request')
        # 如果用户没登录，肯定没收藏
        if not request or not request.user.is_authenticated:
            return False
        # 去收藏表里查一下有没有记录
        return obj.like_by.filter(user=request.user).exists()

    def validate(self, attrs):
        # 默认设置审核中
        status = attrs.get('status', 4)
        # 创建商品限制状态只能是【草稿】或【审核中】！
        if not self.instance and status not in [0, 4]:
            raise serializers.ValidationError({"status": "新创建商品的状态只能是草稿或审核中！"})
        # 状态非草稿规则限制
        if status != 0:
            # 必须有标题
            if not attrs.get('title'):
                raise serializers.ValidationError({"title": "非草稿状态必须填写商品标题！"})

            # 必须有描述
            if not attrs.get('description'):
                raise serializers.ValidationError({"description": "非草稿状态必须填写商品详情！"})

            # 必须有价格
            price = attrs.get('price', 0)
            if price <= 0:
                raise serializers.ValidationError({"price": "商品价格必须大于 0！"})

            delivery_method = attrs.get('delivery_method')
            if delivery_method not in [1, 2, 3]:
                raise serializers.ValidationError({"delivery_method": "请选择合法的发货方式！"})

            category_instance = attrs.get('category')
            if not category_instance:
                raise serializers.ValidationError({"category_id": "非草稿状态必须选择商品分类！"})

            attributes = attrs.get('attributes', {})
            # 分类和属性规范限制
            if category_instance and attributes:

                valid_attr_objs = category_instance.attributes.all()
                valid_attr_map = {obj.name: obj.options for obj in valid_attr_objs}

                for key, value in attributes.items():
                    if key not in valid_attr_map:
                        raise serializers.ValidationError({

                            "attributes": f"非法属性注入拦截：分类【{category_instance.name}】下不存在属性【{key}】！"
                        })

                    valid_options = valid_attr_map[key]
                    if valid_options and value not in valid_options:
                        raise serializers.ValidationError({
                            "attributes": f"非法值注入拦截：属性【{key}】的值只能是 {valid_options} 中的一个！"
                        })

            # 必须有图片
            if not self.instance:
                temp_images = attrs.get('temp_images', [])
                if not temp_images:
                    raise serializers.ValidationError({"temp_images": "发布商品至少需要上传一张图片！"})



        return attrs
    # 重写创建具体实现
    def create(self, validated_data):
        """
        重写 create 方法：实现商品主表与图片的联动保存，并自动清理垃圾文件
        """
        # 剥离出临时图片路径数组（如果前端没传，默认为空列表）
        temp_images = validated_data.pop('temp_images', [])

        # 创建 Goods 主表记录
        # seller字段需要在 View 中通过 serializer.save(seller=request.user)
        goods = Goods.objects.create(**validated_data)

        # 3. 循环处理临时图片，正式入库
        for index, image_path in enumerate(temp_images):
            # 校验临时文件是否真的存在于硬盘上
            if default_storage.exists(image_path):
                # 打开临时图片文件
                with default_storage.open(image_path, 'rb') as f:
                    # 🌟 核心智能逻辑：默认把前端传来的第一张图当作主图 (is_cover=True)
                    is_cover = True if index == 0 else False
                    # 获取文件名
                    file_name = os.path.basename(image_path)
                    # 存入数据库，upload_to="goods/images/%Y/%m/"
                    GoodsImage.objects.create(
                        goods=goods,
                        image=File(f, name=file_name),
                        is_cover=is_cover
                    )
                #硬盘自清洁
                default_storage.delete(image_path)

        return goods
