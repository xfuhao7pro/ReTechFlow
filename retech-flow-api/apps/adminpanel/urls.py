from django.urls import path

from .views import (
    AdminDashboardView,
    AdminAnnouncementDetailView,
    AdminAnnouncementListView,
    AdminCategoryAttributeView,
    AdminCategoryDetailView,
    AdminCategoryListView,
    AdminGoodsListView,
    AdminGoodsStatusView,
    AdminIdentityListView,
    AdminOrderListView,
    AdminUserListView,
    AdminUserPasswordResetView,
    AdminUserVerifyView,
    AdminUserRoleView,
    AdminUserStatusView,
)

app_name = "adminpanel"

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="dashboard"),
    path("goods/", AdminGoodsListView.as_view(), name="goods"),
    path("goods/<str:goods_id>/status/", AdminGoodsStatusView.as_view(), name="goods_status"),
    path("identity/", AdminIdentityListView.as_view(), name="identity"),
    path("orders/", AdminOrderListView.as_view(), name="orders"),
    path("users/", AdminUserListView.as_view(), name="users"),
    path("users/<str:user_id>/reset-password/", AdminUserPasswordResetView.as_view(), name="user_reset_password"),
    path("users/<str:user_id>/verify/", AdminUserVerifyView.as_view(), name="user_verify"),
    path("users/<str:user_id>/role/", AdminUserRoleView.as_view(), name="user_role"),
    path("users/<str:user_id>/status/", AdminUserStatusView.as_view(), name="user_status"),
    path("categories/", AdminCategoryListView.as_view(), name="categories"),
    path("categories/<int:category_id>/", AdminCategoryDetailView.as_view(), name="category_detail"),
    path("categories/<int:category_id>/attributes/", AdminCategoryAttributeView.as_view(), name="category_attribute_create"),
    path(
        "categories/<int:category_id>/attributes/<int:attr_id>/",
        AdminCategoryAttributeView.as_view(),
        name="category_attribute_detail",
    ),
    path("announcements/", AdminAnnouncementListView.as_view(), name="announcements"),
    path("announcements/<int:notice_id>/", AdminAnnouncementDetailView.as_view(), name="announcement_detail"),
]
