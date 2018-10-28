"""
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
"""

from django.urls import path
from bank_accounts.views import home_view, account_create_raw_view, AccountCreateView, AccountListView,\
    account_detail_view, AccountUpdateView

app_name = 'bank_accounts'
urlpatterns = [
    path('', home_view, name='home'),
    path('create/', AccountCreateView.as_view(), name='create'),
    path('create_raw/', account_create_raw_view, name='create_raw'),
    path('<int:pk>/update/', AccountUpdateView.as_view(), name='update'),
    path('user_account_list', AccountListView.as_view(), name='account_list'),

    # DetailView expects a URL argument to determine the model to detail
    # path('<int:pk>/user_account_detail', AccountDetailView.as_view(), name='account_detail'),
    path('<int:pk>/user_account_detail', account_detail_view, name='account_detail'),
]
