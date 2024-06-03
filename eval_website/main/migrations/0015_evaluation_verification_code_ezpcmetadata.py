# Generated by Django 4.2.10 on 2024-04-05 11:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0014_remove_trustedthirdparty_session_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="evaluation",
            name="verification_code",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name="EzPCMetadata",
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
                ("online_computation_time", models.FloatField(default=0)),
                ("offline_computation_time", models.FloatField(default=0)),
                ("Total_computation_time", models.FloatField(default=0)),
                ("metadata", models.TextField()),
                (
                    "evaluation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="main.evaluation",
                    ),
                ),
            ],
        ),
    ]