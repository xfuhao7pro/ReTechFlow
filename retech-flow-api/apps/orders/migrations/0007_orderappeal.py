from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("orders", "0006_rename_goods_image_order_snapshot_image_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrderAppeal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("issue_type", models.CharField(max_length=50, verbose_name="申诉类型")),
                ("description", models.TextField(verbose_name="问题描述")),
                ("original_order_status", models.SmallIntegerField(default=0, verbose_name="申诉前订单状态")),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[(0, "待处理"), (1, "处理中"), (2, "已裁决"), (3, "已关闭")],
                        default=0,
                        verbose_name="申诉状态",
                    ),
                ),
                (
                    "result",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("", "未裁决"),
                            ("refund_buyer", "退款给买家"),
                            ("release_seller", "放款给卖家"),
                            ("close", "关闭申诉"),
                        ],
                        default="",
                        max_length=20,
                        verbose_name="裁决结果",
                    ),
                ),
                ("admin_remark", models.TextField(blank=True, default="", verbose_name="处理备注")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("handled_at", models.DateTimeField(blank=True, null=True, verbose_name="处理时间")),
                (
                    "applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="order_appeals",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="申诉人",
                    ),
                ),
                (
                    "handled_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="handled_order_appeals",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="处理人",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="appeals",
                        to="orders.order",
                        verbose_name="关联订单",
                    ),
                ),
            ],
            options={
                "verbose_name": "订单申诉",
                "verbose_name_plural": "订单申诉",
                "db_table": "second_hand_order_appeal",
                "ordering": ["status", "-created_at"],
            },
        ),
    ]
