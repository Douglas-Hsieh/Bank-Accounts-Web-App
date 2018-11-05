"""
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
"""

from django.urls import path
from bank_accounts.views import home_view, AccountCreateView, AccountListView,\
    account_detail_view, account_update_view, account_delete_view, internal_transfer_view, InternalTransferReceiptList,\
    external_transfer_view

app_name = 'bank_accounts'  # URL Namespace (to distinguish view names such as 'home' and 'bank_accounts:home')
urlpatterns = [
    path('', home_view, name='home'),
    path('create/', AccountCreateView.as_view(), name='create'),
    # path('create_raw/', account_create_raw_view, name='create_raw'),
    path('<int:pk>/update/', account_update_view, name='update'),
    path('<int:pk>/delete/', account_delete_view, name='delete'),
    # path('<int:pk>/delete/', AccountDeleteView.as_view(), name='delete_account'),

    path('user_account_list', AccountListView.as_view(), name='account_list'),
    # DetailView expects a URL argument to determine the model to detail
    # path('<int:pk>/user_account_detail', AccountDetailView.as_view(), name='account_detail'),
    path('<int:pk>/user_account_detail', account_detail_view, name='account_detail'),

    path('internal_transfer', internal_transfer_view, name='internal_transfer'),
    # path('internal_transfer', raw_internal_transfer_view, name='internal_transfer')
    path('internal_transfer_receipt_list', InternalTransferReceiptList.as_view(), name='internal_transfer_receipt_list'),
    path('external_transfer', external_transfer_view, name='external_transfer'),

]
