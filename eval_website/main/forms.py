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