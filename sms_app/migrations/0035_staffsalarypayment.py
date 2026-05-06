# Generated manually on 2026-05-05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sms_app", "0034_staffsalarycomponent"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StaffSalaryPayment",
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
                ("staff_name", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "staff_category",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "salary_month",
                    models.CharField(
                        help_text="Salary month in YYYY-MM format.", max_length=7
                    ),
                ),
                (
                    "basic_salary",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "total_earnings",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                (
                    "total_deductions",
                    models.DecimalField(decimal_places=2, default=0, max_digits=12),
                ),
                ("net_salary", models.DecimalField(decimal_places=2, max_digits=12)),
                ("paid_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "payment_mode",
                    models.CharField(
                        choices=[("online", "Online"), ("offline", "Offline")],
                        max_length=20,
                    ),
                ),
                (
                    "payment_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("paid", "Paid"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="paid",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "paid_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="staff_salary_payments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sms_app.school",
                    ),
                ),
                (
                    "staff",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="salary_payments",
                        to="sms_app.staff",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="staffsalarypayment",
            constraint=models.UniqueConstraint(
                fields=("staff", "salary_month"),
                name="unique_staff_salary_payment_per_month",
            ),
        ),
        migrations.AddIndex(
            model_name="staffsalarypayment",
            index=models.Index(
                fields=["school", "salary_month"],
                name="sal_pay_school_month_idx",
            ),
        ),
    ]
