from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("chats", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemAnnouncement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=80, verbose_name="公告标题")),
                ("content", models.TextField(verbose_name="公告内容")),
                ("is_active", models.BooleanField(default=True, verbose_name="是否启用")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="发布时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_announcements",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="发布人",
                    ),
                ),
            ],
            options={
                "verbose_name": "系统公告",
                "verbose_name_plural": "系统公告",
                "db_table": "system_announcement",
                "ordering": ["-created_at"],
            },
        ),
    ]
