# Generated manually because local settings import is missing dj_database_url.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sms_app", "0023_late_fee_discount_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="academicyear",
            name="start_month",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="academicyear",
            name="end_month",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
