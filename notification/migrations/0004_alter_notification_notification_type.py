# Generated by Django 4.2.16 on 2025-03-19 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0003_alter_notification_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="notification_type",
            field=models.IntegerField(
                choices=[
                    (1, "Like"),
                    (2, "Follow"),
                    (3, "Comment"),
                    (4, "Reply"),
                    (5, "Like-Comment"),
                    (6, "Like-Reply"),
                    (7, "Mentor-Application"),
                ]
            ),
        ),
    ]
