# Generated manually because local settings import is missing dj_database_url.

import django.conf
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
        ("sms_app", "0020_studentfee"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentFeePayment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "payment_mode",
                    models.CharField(
                        choices=[
                            ("cash", "Cash"),
                            ("online", "Online"),
                            ("cheque", "Cheque"),
                            ("bank_transfer", "Bank Transfer"),
                            ("upi", "UPI"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "transaction_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "receipt_number",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("payment_date", models.DateTimeField(blank=True, null=True)),
                ("note", models.TextField(blank=True, null=True)),
                ("is_verified", models.BooleanField(default=False)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "collected_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="collected_fee_payments",
                        to=django.conf.settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "feetype",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sms_app.feetype",
                    ),
                ),
                (
                    "school",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sms_app.school",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fee_payments",
                        to="sms_app.student",
                    ),
                ),
                (
                    "student_fee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="sms_app.studentfee",
                    ),
                ),
                (
                    "verified_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="verified_student_fee_payments",
                        to=django.conf.settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
