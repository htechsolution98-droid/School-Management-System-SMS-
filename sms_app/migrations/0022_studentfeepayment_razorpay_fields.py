# Generated manually because local settings import is missing dj_database_url.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sms_app", "0021_studentfeepayment"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentfeepayment",
            name="razorpay_order_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="studentfeepayment",
            name="razorpay_payment_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="studentfeepayment",
            name="razorpay_signature",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
