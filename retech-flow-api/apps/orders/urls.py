from django.urls import path
from .views import (
    CreateOrderView,
    PayOrderView,
    MyOrderListView,
    MySellOrderListView,
    OrderLogisticsView,
    ShipOrderView,
    ConfirmReceiptView, CancelOrderView,
)
app_name = 'orders'

urlpatterns = [
    # 创单接口
    path('create/', CreateOrderView.as_view(), name='create_order'),
    # 支付接口 (把刚才生成的雪花 64 位字符串传过来)
    path('<str:order_id>/pay/', PayOrderView.as_view(), name='pay_order'),
    path('my/', MyOrderListView.as_view(), name='my_order_list'),
    path('sell/', MySellOrderListView.as_view(), name='my_sell_order_list'),
    path('<str:order_id>/logistics/', OrderLogisticsView.as_view(), name='order_logistics'),
    path('<str:order_id>/ship/', ShipOrderView.as_view(), name='order_ship'),
    path('<str:order_id>/confirm/', ConfirmReceiptView.as_view(), name='order_confirm'),
    path('<str:order_id>/cancel/', CancelOrderView.as_view(), name='order_cancel'),
]