from django.urls import path
from .views import (
    UserLoginView,
    UserProfileView,
    UserSendEmailCodeView,
    UserRegisterView,
    UserResetPasswordView,
    AvatarUploadView,
    AddressListView,
    AddressDetailView,
    UserSecurityView,
    UserWalletView,
    ChangePhoneView,
    RealNameSubmitView,

)
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'users'

urlpatterns = [
    # 登录
    path('login/', UserLoginView.as_view(), name='user-login'),
    # 刷新Token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 查个人信息
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    # 账号与安全
    path('security/', UserSecurityView.as_view(), name='user-security'),
    path('security/realname/', RealNameSubmitView.as_view(), name='realname-submit'),
    # 资产钱包
    path('wallet/', UserWalletView.as_view(), name='user-wallet'),
    # 钱包充值
    path('wallet/recharge/', UserWalletView.as_view(), name='user-wallet-recharge'),
    # 头像路由
    path('avatar/upload/', AvatarUploadView.as_view(), name='avatar-upload'),
    # 发验证码
    path('send-code/', UserSendEmailCodeView.as_view(), name='user-send-code'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
    # 重置密码
    path('resetpwd/', UserResetPasswordView.as_view(), name='user-resetpwd'),
    # 获取我的地址列表 / 新增地址
    path('addresses/', AddressListView.as_view(), name='address-list'),
    # 修改/删除指定地址
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    # 绑定手机号
    path('user/change-phone/', ChangePhoneView.as_view(), name='change_phone'),

]
