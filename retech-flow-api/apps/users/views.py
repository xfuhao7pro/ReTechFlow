import os
import uuid
import logging

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Address, IdentityVerificationStatusChoices
from .serializers import UserLoginSerializer, UserRegisterSerializer, UserResetPasswordSerializer, \
    UserProfileSerializer, AddressSerializer, UserSecuritySerializer, UserWalletSerializer, RealNameSubmitSerializer
from .utils.sendEmailCode import send_email_code
User = get_user_model()
logger = logging.getLogger(__name__)
class UserLoginView(APIView):
    """
    登录接口
    """
    # 访问权限
    permission_classes = [AllowAny]

    def post(self, request):
        # 将数据交给序列化器校验
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # 发token
            refresh = RefreshToken.for_user(user)
            return Response({
                "code": 200,
                "msg": "登录成功！",
                "data": {
                    "access": str(refresh.access_token),  # 返回 Access Token
                    "refresh": str(refresh),  # 返回 Refresh Token
                    "user_info": {
                        "id": user.id,
                        "email": user.email,
                        "nickname": user.nickname,
                        "balance": user.balance,
                        "role": user.role,
                        "is_verified": user.is_verified,
                        "avatar": user.avatar,
                    }
                }
            })
        # 校验失败返回第一条错误信息
        error_msg = list(serializer.errors.values())[0][0] if serializer.errors else "登录失败"
        return Response({
            "code": 400,
             "msg": error_msg,
            "data": None
        },status=400)

class UserSendEmailCodeView(APIView):
    """
    邮箱验证码发送接口
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()

        if not email:
            return Response({'code': 400, 'msg': '邮箱不能为空', 'data': None}, status=400)

        success, msg, cooldown = send_email_code(email)
        status_code = 200 if success else 400

        return Response({
            'code': status_code,
            'msg': msg,
            'data': {'cooldown': cooldown}
        }, status=status_code)

class UserRegisterView(APIView):
    """
    用户注册接口
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 200, "msg": "注册成功！请前往登录", "data": None})

        error_msg = list(serializer.errors.values())[0][0] if serializer.errors else "注册失败"
        return Response({"code": 400, "msg": str(error_msg), "data": None}, status=400)

class UserResetPasswordView(APIView):
    """
    重置密码接口
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": 200,
                "msg": "密码重置成功！请使用新密码登录",
                "data": None
            })

        error_msg = list(serializer.errors.values())[0][0] if serializer.errors else "密码重置失败"
        return Response({"code": 400, "msg": error_msg, "data": None})

class UserProfileView(APIView):
    """获取与修改基础个人资料"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({"code": 200, "data": serializer.data})

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 200, "msg": "资料更新成功", "data": serializer.data})
        return Response({"code": 400, "errors": serializer.errors}, status=400)

class UserSecurityView(APIView):
    """获取账号与安全信息"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSecuritySerializer(request.user)
        # 💡 安全进阶：可以在这里把身份证号脱敏，比如返回 410***********1234
        return Response({"code": 200, "data": serializer.data})


class RealNameSubmitView(APIView):
    """提交实名认证资料，等待后台审核"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RealNameSubmitSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            error_msg = list(serializer.errors.values())[0][0] if serializer.errors else "提交失败"
            return Response({"code": 400, "msg": str(error_msg), "errors": serializer.errors}, status=400)

        user = request.user
        user.real_name = serializer.validated_data["real_name"]
        user.id_card = serializer.validated_data["id_card"]
        user.is_verified = False
        user.verification_status = IdentityVerificationStatusChoices.PENDING
        user.verification_reject_reason = ""
        user.save(update_fields=[
            "real_name", "id_card", "is_verified",
            "verification_status", "verification_reject_reason"
        ])
        return Response({
            "code": 200,
            "msg": "实名认证资料已提交，请等待平台审核",
            "data": UserSecuritySerializer(user).data,
        })

class UserWalletView(APIView):
    """获取资产钱包信息 & 充值"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserWalletSerializer(request.user)
        return Response({"code": 200, "data": serializer.data})

    def post(self, request):
        """模拟充值接口"""
        if not settings.ENABLE_MOCK_RECHARGE:
            return Response({"code": 403, "msg": "生产环境未启用模拟充值"}, status=403)

        amount = request.data.get('amount')
        try:
            from decimal import Decimal
            amount = Decimal(str(amount))
            if amount <= 0:
                return Response({"code": 400, "msg": "充值金额必须大于0"})
            if amount > Decimal("100000"):
                return Response({"code": 400, "msg": "单次充值金额不能超过 100000 元"})
        except (TypeError, ValueError):
            return Response({"code": 400, "msg": "充值金额格式不正确"})

        # 开启事务，加锁更新余额
        with transaction.atomic():
            user = User.objects.select_for_update().get(id=request.user.id)
            user.balance += amount
            user.save()

        return Response({
            "code": 200,
            "msg": f"成功充值 {amount} 元",
            "data": {"balance": user.balance}
        })

class AvatarUploadView(APIView):
    """
    用户自定义头像上传接口
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. 从请求中获取名为 'file' 的图片数据
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"code": 400, "msg": "请选择要上传的图片"}, status=400)

        # 2. 校验文件大小 (比如限制为 2MB)
        if file_obj.size > 2 * 1024 * 1024:
            return Response({"code": 400, "msg": "头像图片不能超过 2MB"}, status=400)

        # 3. 校验后缀名，防止上传恶意脚本
        ext = os.path.splitext(file_obj.name)[-1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            return Response({"code": 400, "msg": "只支持 JPG/PNG/WEBP 格式"}, status=400)

        # 4. 生成唯一文件名（防重名覆盖）
        # 格式类似：avatars/2026/用户ID_随机码.jpg
        new_filename = f"avatars/{request.user.id}_{uuid.uuid4().hex[:8]}{ext}"

        # 5. 保存文件到硬盘 (存入 Django 配置的 MEDIA_ROOT 目录下)
        saved_path = default_storage.save(new_filename, file_obj)

        # 6. 返回相对路径给前端
        return Response({
            "code": 200,
            "msg": "上传成功",
            "data": {
                "url": saved_path  # 比如返回 "avatars/1_a1b2c3d4.jpg"
            }
        })

class AddressListView(APIView):
    """
    地址列表 & 新增地址
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 查出我的所有地址
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response({"code": 200, "data": serializer.data})

    @transaction.atomic  # 开启事务保证数据一致性
    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            is_default = serializer.validated_data.get('is_default', False)

            # 如果这是用户的第一条地址，强制设为默认
            if not Address.objects.filter(user=request.user).exists():
                is_default = True

            # 如果当前这条设为默认，把其他的都取消默认
            if is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

            serializer.save(user=request.user, is_default=is_default)
            return Response({"code": 200, "msg": "地址添加成功", "data": serializer.data})

        return Response({"code": 400, "msg": "参数错误", "errors": serializer.errors}, status=400)

class AddressDetailView(APIView):
    """
    修改/删除地址
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        address = get_object_or_404(Address, id=pk, user=request.user)
        serializer = AddressSerializer(address, data=request.data, partial=True)

        if serializer.is_valid():
            is_default = serializer.validated_data.get('is_default', address.is_default)
            # 如果修改为默认地址，排他处理
            if is_default and not address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

            serializer.save(is_default=is_default)
            return Response({"code": 200, "msg": "地址修改成功", "data": serializer.data})

        return Response({"code": 400, "msg": "参数错误", "errors": serializer.errors}, status=400)

    def delete(self, request, pk):
        address = get_object_or_404(Address, id=pk, user=request.user)
        address.delete()

        # =如果删掉的是默认地址，就把剩下的最新一条设为默认
        if address.is_default:
            last_address = Address.objects.filter(user=request.user).first()
            if last_address:
                last_address.is_default = True
                last_address.save()

        return Response({"code": 200, "msg": "地址删除成功"})


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePhoneSerializer


class ChangePhoneView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePhoneSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "code": 400,
                "msg": "输入信息有误",
                "errors": serializer.errors
            }, status=400)

        data = serializer.validated_data
        user = request.user

        if not user.check_password(data['password']):
            return Response({"code": 400, "msg": "原始密码校验失败"}, status=400)
        try:
            user.telephone = data['phone']
            user.save()
            return Response({
                "code": 200,
                "msg": "手机号修改成功",
                "data": {"phone": user.telephone}
            })
        except Exception:
            logger.exception("Failed to change phone for user %s", request.user.id)
            return Response({"code": 500, "msg": "服务器内部错误，请稍后重试"}, status=500)
