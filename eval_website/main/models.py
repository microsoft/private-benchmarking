# 
# Author: Tanmay Rajore
# 
# Copyright:
# 
# Copyright (c) 2024 Microsoft Research
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from datetime import datetime
import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

def validate_file_size(value):
    max_size_mb = 1
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    filesize = value.size
    if filesize > max_size_bytes:
        max_size_mb_display = max_size_mb
        raise ValidationError(
            _('The maximum file size allowed is %(max_size_mb)s MB.'),
            params={'max_size_mb': max_size_mb_display},
        )
        
class ModelArchitecture(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=5000, blank=False, help_text="This field supports markdown.")
    def architecture_file_upload_path(instance, filename):
        username = instance.user.username
        model_id = uuid.uuid4()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f'model_architectures/modelconfig_{username}_{model_id}_{timestamp}.json'
    architecture_file = models.FileField(upload_to=architecture_file_upload_path, validators=[FileExtensionValidator(allowed_extensions=['json']),validate_file_size], blank=False, null=False)

    def docker_file_upload_path(instance, filename):
        username = instance.user.username
        model_id = uuid.uuid4()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f'docker_files/docker_{username}_{model_id}_{timestamp}.Dockerfile'

    docker_file = models.FileField(upload_to=docker_file_upload_path, validators=[FileExtensionValidator(allowed_extensions=['Dockerfile','DOCKERFILE']),validate_file_size], blank=False, null=False)

    def __str__(self):
        return self.name
    
class Dataset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def dataset_metadata_upload_path(instance, filename):
        username = instance.user.username
        dataset_id = uuid.uuid4()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f'datasets_metadata/dataset_{username}_{dataset_id}_{timestamp}.txt'
    dataset_metadata = models.FileField(upload_to=dataset_metadata_upload_path, validators=[FileExtensionValidator(allowed_extensions=['txt']),validate_file_size],blank=False, null=False)

    def __str__(self):
        return self.name

def generate_verification_code(architecture_choosen):
    if architecture_choosen==3 or architecture_choosen==4 or architecture_choosen==5:
        verification_code = uuid.uuid4().hex
        return verification_code
    else:
        return None

class Evaluation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ForeignKey(ModelArchitecture, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    status = models.CharField(max_length=20, default='Pending')
    is_approved_by_model_owner = models.BooleanField(default=False)
    is_approved_by_dataset_owner = models.BooleanField(default=False)
    architecture_choosen=models.IntegerField(default=1)
    cost = models.FloatField(default=0, validators=[MinValueValidator(0)])
    verification_code = models.CharField(default=generate_verification_code(architecture_choosen),max_length=100, blank=True, null=True)
    if architecture_choosen==1 or architecture_choosen==2:
        cost=0
    def __str__(self):
        return f'Evaluation of {self.model} using {self.dataset} by {self.user} using {self.architecture_choosen}'

class EzPCMetadata(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    online_computation_time=models.FloatField(default=0)
    offline_computation_time=models.FloatField(default=0)
    Total_computation_time=models.FloatField(default=0)
    metadata=models.TextField()
    def __str__(self):
        return f'Metadata of {self.evaluation}'
    

class LeaderboardEntry(models.Model):
    model_name = models.ForeignKey(ModelArchitecture, on_delete=models.CASCADE)
    model_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    Method_used=models.IntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.model_owner.username}: {self.accuracy}'
    
class TrustedThirdParty(models.Model):
    Name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    auth_token = models.CharField(max_length=100)
    def __str__(self):
        return f'Trusted Third Party: {self.Name}'

class confidential_compute(models.Model):
    Name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    auth_token = models.CharField(max_length=100)
    def __str__(self):
        return f'Confidential compute: {self.Name}'

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField(default=0, validators=[MinValueValidator(0)])
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}: {self.amount}'

    @classmethod
    def update_amount(cls):
        users = User.objects.all()
        for user in users:
            total_cost = Evaluation.objects.filter(user=user).aggregate(total_cost=Sum('cost'))['total_cost']
            if total_cost is not None:
                expense, created = Expense.objects.get_or_create(user=user)
                expense.amount = total_cost
                expense.save()

@receiver(post_save, sender=Evaluation)
def update_expense_amount(sender, instance, created, **kwargs):
    if created:
        Expense.update_amount()