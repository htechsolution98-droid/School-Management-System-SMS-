# Generated manually on 2026-05-05

from django.db import migrations, models
import django.utils.timezone


def populate_attendance_date(apps, schema_editor):
    Attendance = apps.get_model("sms_app", "Attendance")

    for attendance in Attendance.objects.all().iterator():
        if attendance.date_time:
            attendance.attendance_date = attendance.date_time.date()
        else:
            attendance.attendance_date = django.utils.timezone.localdate()
        attendance.save(update_fields=["attendance_date"])


class Migration(migrations.Migration):

    dependencies = [
        ("sms_app", "0029_attendance_is_half_day"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendance",
            name="attendance_date",
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
        migrations.RunPython(populate_attendance_date, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="attendance",
            name="attendance_date",
            field=models.DateField(
                db_index=True, default=django.utils.timezone.localdate
            ),
        ),
        migrations.AddConstraint(
            model_name="attendance",
            constraint=models.UniqueConstraint(
                fields=("staff", "attendance_date"),
                name="unique_staff_attendance_per_day",
            ),
        ),
        migrations.AddIndex(
            model_name="attendance",
            index=models.Index(
                fields=["school", "attendance_date"],
                name="attendance_school_date_idx",
            ),
        ),
    ]
