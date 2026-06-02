from django.core.management.base import BaseCommand
from apps.chats.models import ChatSession


class Command(BaseCommand):
    help = '一键清空所有聊天会话和消息记录'

    def add_arguments(self, parser):
        # 增加一个 --force 参数，防止误删
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制删除，不再询问',
        )

    def handle(self, *args, **options):
        # 如果没有带 --force 参数，先弹窗确认一下
        if not options['force']:
            confirm = input("⚠️  确定要清空所有聊天数据吗？此操作不可恢复！(y/n): ")
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('操作已取消'))
                return

        # 执行删除逻辑
        count, _ = ChatSession.objects.all().delete()

        # 打印成功信息
        self.stdout.write(
            self.style.SUCCESS(f'成功！清空了 {count} 条会话及其关联的消息记录。')
        )