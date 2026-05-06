# Generated manually on 2026-05-05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sms_app", "0035_staffsalarypayment"),
    ]

    operations = [
        migrations.AddField(
            model_name="staffsalarypayment",
            name="attendance_deduction",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name="staffsalarypayment",
            name="component_snapshot",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="staffsalarypayment",
            name="working_days",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="staffsalarypayment",
            name="present_days",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name="staffsalarypayment",
            name="absent_days",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="staffsalarypayment",
            name="half_days",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
