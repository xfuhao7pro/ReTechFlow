import shortuuid
from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from .utils import randomUserNickname
from django.conf import settings


def generate_short_uuid():
    return shortuuid.uuid()


# 角色枚举
class UserRoleChoices(models.IntegerChoices):
    NORMAL_USER = 1, "普通用户"
    AUDITOR = 2, "平台审核员"
    ADMIN = 3, "系统管理员"


# 自定义用户管理器 (适配邮箱 Email 登录)
class PlatformUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("必须设置邮箱地址")

        # 邮箱地址标准化（转小写等）
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", UserRoleChoices.NORMAL_USER)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRoleChoices.ADMIN)
        extra_fields.setdefault("is_verified", True)  # 管理员默认已认证

        if extra_fields.get("is_staff") is not True:
            raise ValueError("超级管理员必须设置 is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("超级管理员必须设置 is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


# 重写 User 表
class PlatformUser(AbstractBaseUser, PermissionsMixin):
    """
    二手3C交易平台 用户模型
    使用 Email 作为唯一登录标识
    绑定id 使用uuid
    """
    id = models.CharField(
        primary_key=True,
        max_length=22,
        default=generate_short_uuid,
        editable=False,
    )

    # 基础信息
    email = models.EmailField("邮箱", unique=True, max_length=100)
    telephone = models.CharField("联系电话", max_length=11, blank=True)  # 仅作展示和联系使用，不作为登录凭证
    nickname = models.CharField("昵称", max_length=30, blank=True, default=randomUserNickname.generate_default_nickname)
    avatar = models.CharField('头像', max_length=100, default='avatars/default_01.png', blank=True)

    bio = models.CharField('个性签名', max_length=200, blank=True, default='这个人很懒，什么都没写~')

    gender = models.SmallIntegerField('性别', choices=((0, '保密'), (1, '男'), (2, '女')), default=0)
    # 常驻城市
    location = models.CharField('所在城市', max_length=50, blank=True, null=True)

    # 认证与业务字段
    real_name = models.CharField("真实姓名", max_length=20, blank=True)
    id_card = models.CharField("身份证号", max_length=18, blank=True)
    role = models.IntegerField("系统角色", choices=UserRoleChoices.choices,
                               default=UserRoleChoices.NORMAL_USER)
    is_verified = models.BooleanField("实名认证状态", default=False)
    balance = models.DecimalField("账户余额", max_digits=10, decimal_places=2, default=0.00)

    # Django 权限与状态字段
    is_staff = models.BooleanField("后台登录权限", default=False)
    is_active = models.BooleanField("账号是否激活", default=True)
    date_joined = models.DateTimeField("注册时间", auto_now_add=True)

    objects = PlatformUserManager()

    # 指定邮箱为登录认证字段
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'second_hand_user'
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        role_display = dict(UserRoleChoices.choices).get(self.role, "未知角色")
        return f"{self.email} ({role_display})"

    def clean(self):
        super().clean()
        # 数据清洗
        self.email = self.__class__.objects.normalize_email(self.email)

# 地址模型
class Address(models.Model):
    """
    用户收发货地址表
    """
    user = models.ForeignKey('PlatformUser', on_delete=models.CASCADE, related_name='addresses')

    receiver_name = models.CharField("联系人姓名", max_length=20)
    telephone = models.CharField("手机号", max_length=11)

    province = models.CharField("省", max_length=50)
    city = models.CharField("市", max_length=50)
    district = models.CharField("区/县", max_length=50)
    detail_address = models.CharField("详细地址", max_length=200)

    is_default = models.BooleanField("默认收货地址", default=False)
    is_default_return = models.BooleanField("默认退货/发货地址", default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'second_hand_user_address'
        # 按收货默认、发货默认排在最前面
        ordering = ['-is_default', '-is_default_return', '-updated_at']
