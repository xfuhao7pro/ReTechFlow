import shortuuid
from django.db import models
from django.conf import settings

def generate_short_uuid():
    return shortuuid.uuid()



class ChatSession(models.Model):
    id = models.CharField(primary_key=True, max_length=22, default=generate_short_uuid, editable=False)

    goods = models.ForeignKey('goods.Goods', on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='关联商品')
    initiator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='initiated_sessions')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_sessions')
    last_message = models.TextField('最后一条消息', blank=True)
    last_message_at = models.DateTimeField('最后消息时间', auto_now_add=False, default=None, null=True, blank=True)
    unread_initiator = models.IntegerField('发起方未读数', default=0)
    unread_receiver = models.IntegerField('接收方未读数', default=0)
    status = models.SmallIntegerField('状态', default=0, choices=((0, '正常'), (1, '屏蔽'), (2, '关闭')))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 同一商品下，买家卖家只有一个活跃会话 (这里改成了 'goods' 对应上面的外键字段名)
        unique_together = ('goods', 'initiator', 'receiver')
        verbose_name = '聊天会话'
        db_table = 'second_hand_chat_session'
        verbose_name_plural = verbose_name


class ChatMessage(models.Model):
    id = models.CharField(primary_key=True, max_length=22, default=generate_short_uuid, editable=False)

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=(('text', '文本'), ('image', '图片'), ('system', '系统')),
                                    default='text')
    content = models.TextField('消息内容')  # 文本或图片相对路径
    send_status = models.SmallIntegerField('发送状态', default=1, choices=((0, 'pending'), (1, 'sent'), (2, 'failed')))
    is_read = models.BooleanField('是否已读', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = '消息聊天'
        db_table = 'second_hand_message'
        verbose_name_plural = verbose_name


class SystemAnnouncement(models.Model):
    title = models.CharField("公告标题", max_length=80)
    content = models.TextField("公告内容")
    is_active = models.BooleanField("是否启用", default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_announcements",
        verbose_name="发布人",
    )
    created_at = models.DateTimeField("发布时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        db_table = "system_announcement"
        ordering = ["-created_at"]
        verbose_name = "系统公告"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
