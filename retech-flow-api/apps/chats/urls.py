from django.urls import path
from .views import (
    SessionViewSet,
    MessageListView,
    MarkReadView, SendMessageView
)
app_name = 'chats'

urlpatterns = [
    # GET  /chats/sessions/获取当前用户的所有聊天列表
    # POST /chats/sessions/点击“联系卖家”时创建或获取会话ID
    path('sessions/', SessionViewSet.as_view(), name='session_list_create'),
    # GET  /chats/sessions/<uuid>/messages/获取指定会话的所有历史聊天记录
    path('sessions/<str:session_id>/messages/', MessageListView.as_view(), name='message_list'),

    # 标记已读
    path('sessions/<str:session_id>/read/', MarkReadView.as_view(), name='mark_read'),
    path('messages/', SendMessageView.as_view(), name='send_message'),

]