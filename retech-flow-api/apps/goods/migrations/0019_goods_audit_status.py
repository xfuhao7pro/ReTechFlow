from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("goods", "0018_alter_goods_id_alter_goodsimage_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="goods",
            name="status",
            field=models.IntegerField(
                choices=[
                    (0, "草稿"),
                    (1, "在售中"),
                    (2, "已售出"),
                    (3, "已下架"),
                    (4, "审核中"),
                    (5, "审核驳回"),
                ],
                default=1,
                verbose_name="商品状态",
            ),
        ),
        migrations.AddField(
            model_name="goods",
            name="audit_reason",
            field=models.CharField(default="", blank=True, max_length=200, verbose_name="审核备注"),
        ),
    ]
