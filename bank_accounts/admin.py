from django.contrib import admin
from .models import Account
# Register your models here.


class AccountAdmin(admin.ModelAdmin):
    model = Account

    fields = ('account_type', 'creator', 'holder', 'balance', 'bank', 'routing_number')  # what admin can change

    # what is displayed in the admin/bank_accounts/account page
    list_display = ['account_type', 'creator', 'holder', 'balance', 'bank', 'routing_number']


admin.site.register(Account, AccountAdmin)
