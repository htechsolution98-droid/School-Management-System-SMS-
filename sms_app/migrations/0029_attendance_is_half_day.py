# Generated manually on 2026-05-05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sms_app", "0028_attendance_check_in_attendance_check_out"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendance",
            name="is_half_day",
            field=models.BooleanField(default=False),
        ),
    ]
