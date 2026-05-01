# Generated manually because local settings import is missing dj_database_url.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sms_app", "0022_studentfeepayment_razorpay_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="feewiseclass",
            name="late_fee_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="feewiseclass",
            name="grace_days",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="feewiseclass",
            name="late_fee_type",
            field=models.CharField(
                blank=True,
                choices=[("fixed", "Fixed"), ("per_day", "Per Day")],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="feewiseclass",
            name="late_fee_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="feewiseclass",
            name="max_late_fee",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="studentfee",
            name="discount_reference",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="studentfee",
            name="discount_note",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="studentfee",
            name="late_fee_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="studentfee",
            name="grace_days",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="studentfee",
            name="late_fee_type",
            field=models.CharField(
                blank=True,
                choices=[("fixed", "Fixed"), ("per_day", "Per Day")],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="studentfee",
            name="late_fee_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="studentfee",
            name="max_late_fee",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
