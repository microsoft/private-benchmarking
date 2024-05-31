# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
from django.urls import path
from . import views

app_name = "main"   


urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path('accounts/login/', views.login_request, name='login'),
    path("logout", views.logout_request, name= "logout"),
    path('options/', views.options, name='options'),
    path('add_model_architecture/', views.add_model_architecture, name='add_model_architecture'),
    path('add_dataset/', views.add_dataset, name='add_dataset'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('model/<int:model_id>/', views.model_detail, name='model_detail'),
    path('evaluate/<int:model_id>/', views.evaluate_model, name='evaluate_model'),
    path('dataset/<int:dataset_id>/', views.dataset_detail, name='dataset_detail'),
    path('login-redirect/', views.login_redirect, name='login_redirect'),
    path('user_profile/<int:user_id>/', views.user_profile, name='user_profile'),
    # URL for downloading script
    path('download_script/<int:request_id>/', views.download_script, name='download_script'),
    path('send_request/<int:model_id>/', views.send_request, name='send_request'),
    path('evaluate_request_response/<int:request_id>/', views.evaluate_request_response, name='evaluate_request_response'),  
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('leaderboard/update', views.update_leaderboard, name='update_leaderboard'),
    path('evaluation/ezpc_metadata', views.ezpc_metadata, name='ezpc_metadata'),
    path('architecture/<int:architecture_id>', views.evaluation_architecture_details, name='evaluation_architecture_detail'),
    
]