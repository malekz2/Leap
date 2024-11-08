# Generated by Django 5.1.1 on 2024-10-03 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_auto_20210403_2153"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="learn",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="profile",
            name="teach",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="relationship",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
