"""
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
"""

from django.urls import path
from accounts.views import home_view, account_create_view, account_create_raw_view

app_name = 'accounts'
urlpatterns = [
    path('', home_view, name='home'),
    path('create/', account_create_view, name='create'),
    path('create_raw/', account_create_raw_view, name='create_raw')
]
