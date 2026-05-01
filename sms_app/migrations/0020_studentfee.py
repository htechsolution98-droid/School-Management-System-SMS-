# Generated manually because local settings import is missing dj_database_url.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sms_app", "0019_feewiseclass"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentFee",
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
                (
                    "billing_period",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Example: 2026-04 for monthly, Q1 for quarterly, or blank for single fees.",
                        max_length=20,
                    ),
                ),
                (
                    "amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "discount_amount",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "fine_amount",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                (
                    "paid_amount",
                    models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
                ("due_date", models.DateField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("partial", "Partial"),
                            ("paid", "Paid"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                (
                    "payment_mode",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "transaction_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                (
                    "academic_year",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sms_app.academicyear",
                    ),
                ),
                (
                    "fee_wise_class",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="sms_app.feewiseclass",
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
                        related_name="student_fees",
                        to="sms_app.student",
                    ),
                ),
            ],
            options={
                "unique_together": {
                    ("student", "feetype", "academic_year", "billing_period")
                },
            },
        ),
    ]
