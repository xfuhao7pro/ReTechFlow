from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0018_alter_platformuser_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="platformuser",
            name="verification_status",
            field=models.IntegerField(
                choices=[(0, "未提交"), (1, "待审核"), (2, "已通过"), (3, "已驳回")],
                default=0,
                verbose_name="实名认证审核状态",
            ),
        ),
        migrations.AddField(
            model_name="platformuser",
            name="verification_reject_reason",
            field=models.CharField(default="", blank=True, max_length=200, verbose_name="实名认证驳回原因"),
        ),
    ]
