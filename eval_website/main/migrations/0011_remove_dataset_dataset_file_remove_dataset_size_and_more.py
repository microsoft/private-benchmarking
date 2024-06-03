# Generated by Django 4.2.10 on 2024-03-18 11:03

import django.core.validators
from django.db import migrations, models
import main.models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0010_remove_leaderboardentry_computation_time"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dataset",
            name="dataset_file",
        ),
        migrations.RemoveField(
            model_name="dataset",
            name="size",
        ),
        migrations.AddField(
            model_name="dataset",
            name="dataset_metadata",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=main.models.Dataset.dataset_metadata_upload_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["txt"]
                    ),
                    main.models.validate_file_size,
                ],
            ),
        ),
        migrations.AddField(
            model_name="modelarchitecture",
            name="docker_file",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=main.models.ModelArchitecture.docker_file_upload_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["Dockerfile", "DOCKERFILE"]
                    ),
                    main.models.validate_file_size,
                ],
            ),
        ),
        migrations.AlterField(
            model_name="modelarchitecture",
            name="architecture_file",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=main.models.ModelArchitecture.architecture_file_upload_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["json"]
                    ),
                    main.models.validate_file_size,
                ],
            ),
        ),
    ]