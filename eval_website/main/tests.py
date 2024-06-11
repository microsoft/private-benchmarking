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

# # Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from main.models import ModelArchitecture, Dataset, Evaluation

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.model = ModelArchitecture.objects.create(name='test_model', user=self.user)
        self.dataset = Dataset.objects.create(name='test_dataset', user=self.user)
        self.evaluation = Evaluation.objects.create(user=self.user, model=self.model, dataset=self.dataset,ip_address='127.0.0.1',port=8000)

    def test_homepage(self):
        response = self.client.get(reverse('main:homepage'))
        self.assertEqual(response.status_code, 200)

    def test_register_request(self):
        response = self.client.get(reverse('main:register'))
        self.assertEqual(response.status_code, 200)

    def test_login_request(self):
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_request(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('main:logout'))
        self.assertEqual(response.status_code, 302)  # Should redirect after logout
    
    def test_profile_request(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('main:user_profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
