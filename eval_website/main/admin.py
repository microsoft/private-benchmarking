# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from django.contrib import admin

# Register your models here.
from .models import ModelArchitecture, Dataset, Evaluation, LeaderboardEntry

admin.site.register(ModelArchitecture)
admin.site.register(Dataset)
admin.site.register(Evaluation)
admin.site.register(LeaderboardEntry)
