# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ModelArchitecture
from .models import Dataset
from .models import Evaluation

# Create your forms here.

class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user
	
class ModelArchitectureForm(forms.ModelForm):
    class Meta:
        model = ModelArchitecture
        fields = ['name', 'description', 'architecture_file', 'docker_file']
        widgets = {
            'architecture_file': forms.FileInput(attrs={'accept': '.json'}),
            'docker_file': forms.FileInput(attrs={'accept': '.Dockerfile,.DOCKERFILE'}),
        }
    def __init__(self, *args, **kwargs):
        super(ModelArchitectureForm, self).__init__(*args, **kwargs)
        self.fields['architecture_file'].required = False
        self.fields['docker_file'].required = False

class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'description', 'dataset_metadata']
        widgets = {
            'dataset_metadata': forms.FileInput(attrs={'accept': '.txt'}),
        }
    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        self.fields['dataset_metadata'].required = False

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['dataset', 'ip_address', 'port', 'architecture_choosen']

    def __init__(self, *args, **kwargs):
        super(EvaluationForm, self).__init__(*args, **kwargs)
        self.fields['dataset'].empty_label = None
        self.fields['ip_address'].required = True
        self.fields['port'].required = True
        self.fields['architecture_choosen'].required = True
        self.fields['architecture_choosen'].type = 'number'