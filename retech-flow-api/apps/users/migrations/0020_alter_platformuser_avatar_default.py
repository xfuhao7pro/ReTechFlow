import apps.users.utils.defaultAvatar
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0019_identity_verification_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="platformuser",
            name="avatar",
            field=models.CharField(
                blank=True,
                default=apps.users.utils.defaultAvatar.random_default_avatar,
                max_length=100,
                verbose_name="头像",
            ),
        ),
    ]
