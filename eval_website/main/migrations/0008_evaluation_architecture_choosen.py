# Generated by Django 4.2.10 on 2024-03-11 08:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0007_evaluation_is_approved_by_dataset_owner_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="evaluation",
            name="architecture_choosen",
            field=models.IntegerField(default=1),
        ),
    ]
