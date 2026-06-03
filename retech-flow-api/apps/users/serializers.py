from datetime import date
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .utils.verifyEmailCode import verify_email_code
from .utils.checkPwd import validate_password_strength
from .models import Address, IdentityVerificationStatusChoices

User = get_user_model()

ID_CARD_WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
ID_CARD_CHECK_CODES = "10X98765432"


def validate_china_id_card(id_card: str) -> tuple[bool, str]:
    value = id_card.upper()
    if len(value) != 18 or not value[:17].isdigit() or value[-1] not in "0123456789X":
        return False, "请输入18位身份证号码"
    if value[:2] == "00":
        return False, "身份证地址码不正确"
    try:
        birth = date(int(value[6:10]), int(value[10:12]), int(value[12:14]))
    except ValueError:
        return False, "身份证出生日期不正确"
    if birth < date(1900, 1, 1) or birth > date.today():
        return False, "身份证出生日期不正确"
    total = sum(int(value[index]) * weight for index, weight in enumerate(ID_CARD_WEIGHTS))
    if ID_CARD_CHECK_CODES[total % 11] != value[-1]:
        return False, "身份证校验码不正确"
    return True, ""

# 公共密码邮箱序列化
class BaseAuthSerializer(serializers.Serializer):
    """
    提取共用的email和password字段及规则
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": "邮箱是必填项哦！",
            "invalid": "这不是一个合法的邮箱格式！",
            "blank": "邮箱不能为空！",
        },
    )
    password = serializers.CharField(
        write_only=True, required=True, max_length=20, min_length=6,
        error_messages={
            "required": "请填写密码！",
            "blank": "密码不能为空！",
            "min_length": "密码长度不能少于六位！",
            "max_length": "密码长度不能超过二十位！",
        }
    )

    def validate_password(self, value):
        # 共用的密码强度校验
        success, msg = validate_password_strength(value)
        if not success:
            raise serializers.ValidationError(msg)
        return value

# 登录序列化
class UserLoginSerializer(BaseAuthSerializer):
    def validate_password(self, value):
        # 登录只校验密码是否匹配，不再套用注册/重置密码的强度规则。
        return value

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError("邮箱错误！该邮箱尚未注册！")
        if not user.check_password(password):
            raise serializers.ValidationError("密码错误！请重新输入！")
        if not user.is_active:
            raise serializers.ValidationError("该账号已被禁用，请联系平台管理员！")

        attrs["user"] = user
        return attrs

# 基类验证码序列化
class BaseCodeAuthSerializer(BaseAuthSerializer):
    password_confirm = serializers.CharField(
        write_only=True, required=True, max_length=20, min_length=6,
        error_messages={"required": "请确认密码！", "blank": "确认密码不能为空！"}
    )
    auth_code = serializers.CharField(
        required=True, max_length=6, min_length=6,
        error_messages={"required": "请填写邮箱验证码！", "blank": "验证码不能为空！"}
    )

    def validate(self, attrs):
        # 1. 校验两次密码是否一致
        password = attrs["password"]
        password_confirm = attrs.pop("password_confirm")  # pop掉不存入数据库
        if password != password_confirm:
            raise serializers.ValidationError("两次输入的密码不一致，请重新输入!")

        # 2. 校验验证码
        email = attrs['email']
        auth_code = attrs.pop('auth_code')
        success, msg = verify_email_code(email, auth_code)
        if not success:
            raise serializers.ValidationError(msg)

        return attrs

# 注册序列化
class UserRegisterSerializer(BaseCodeAuthSerializer):
    def validate_email(self, value):
        # 注册专属：邮箱不能存在
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱已被注册，请直接登录')
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

# 重置密码序列化
class UserResetPasswordSerializer(BaseCodeAuthSerializer):
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('该邮箱未注册，请先检查是否输入正确！')
        return value

    def save(self, **kwargs):
        # 覆盖保存逻辑为修改密码
        email = self.validated_data['email']
        new_password = self.validated_data['password']

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return user

# 用户个人资料序列化
class UserProfileSerializer(serializers.ModelSerializer):
    """
    1. 个人资料序列化器 (完全公开的社交属性)
    对应前端：【个人资料】Tab
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'nickname', 'avatar', 'bio', 'gender', 'location', 'telephone', 'date_joined', 'is_verified']
        read_only_fields = ['id', 'email', 'telephone', 'date_joined', 'is_verified']


class UserSecuritySerializer(serializers.ModelSerializer):
    """
    2. 账号与安全序列化器 (极其私密)
    对应前端：【账号与安全】Tab
    """
    class Meta:
        model = User
        fields = [
            'email', 'telephone', 'real_name', 'id_card', 'is_verified',
            'verification_status', 'verification_reject_reason'
        ]
        # 注意：身份证、真实姓名一旦认证不让改，邮箱修改要走专门的验证码接口
        read_only_fields = [
            'email', 'is_verified', 'real_name', 'id_card',
            'verification_status', 'verification_reject_reason'
        ]


class RealNameSubmitSerializer(serializers.Serializer):
    real_name = serializers.CharField(required=True, min_length=2, max_length=20)
    id_card = serializers.CharField(required=True, min_length=18, max_length=18)

    def validate_id_card(self, value):
        success, msg = validate_china_id_card(value)
        if not success:
            raise serializers.ValidationError(msg)
        return value.upper()

    def validate(self, attrs):
        user = self.context['request'].user
        if user.is_verified or user.verification_status == IdentityVerificationStatusChoices.APPROVED:
            raise serializers.ValidationError("您已完成实名认证，无需重复提交")
        if user.verification_status == IdentityVerificationStatusChoices.PENDING:
            raise serializers.ValidationError("实名认证正在审核中，请勿重复提交")
        return attrs


class UserWalletSerializer(serializers.ModelSerializer):
    """
    3. 资产钱包序列化器 (只管钱)
    对应前端：【资产钱包】Tab
    """
    class Meta:
        model = User
        fields = ['balance']
        read_only_fields = ['balance']  # 绝对不能通过直接提交来修改余额！


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    def validate_telephone(self, value):
        if len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError("请输入正确的11位手机号！")
        return value

# 绑定手机号
class ChangePhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11, min_length=11)
    password = serializers.CharField(write_only=True) # 改手机号通常要求输一下密码确认身份

    def validate_phone(self, value):
        # 检查这个手机号是不是已经被别人占用了
        if User.objects.filter(telephone=value).exists():
            raise serializers.ValidationError("该手机号已被其他账号绑定")
        return value
