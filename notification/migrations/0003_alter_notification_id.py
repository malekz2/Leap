# Generated by Django 5.1.1 on 2024-10-13 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0002_auto_20210201_1854"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
