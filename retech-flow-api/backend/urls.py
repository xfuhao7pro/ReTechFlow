from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("apps.users.urls", namespace="users")),
    path("goods/", include("apps.goods.urls", namespace="goods")),
    path("chats/", include("apps.chats.urls", namespace="chats")),
    path("orders/", include("apps.orders.urls", namespace="orders")),
    path("platform-admin/", include("apps.adminpanel.urls", namespace="adminpanel")),

]

# 代理返回图片文件
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
