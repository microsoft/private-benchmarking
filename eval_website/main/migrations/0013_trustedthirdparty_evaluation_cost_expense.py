# Generated by Django 4.2.10 on 2024-03-27 07:52

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("main", "0012_remove_leaderboardentry_change_in_rank_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TrustedThirdParty",
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
                ("Name", models.CharField(max_length=100)),
                ("ip_address", models.GenericIPAddressField()),
                ("port", models.PositiveIntegerField()),
                ("auth_token", models.CharField(max_length=100)),
                ("session_id", models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name="evaluation",
            name="cost",
            field=models.FloatField(
                default=0, validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        migrations.CreateModel(
            name="Expense",
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
                    "amount",
                    models.FloatField(
                        default=0,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_updated", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
