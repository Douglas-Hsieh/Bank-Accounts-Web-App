from django.contrib import admin
from .models import Account
# Register your models here.


class AccountAdmin(admin.ModelAdmin):
    model = Account
    fields = ('type','balance', 'bank')  # what admin can change
    list_display = ['type', 'owner']  # what is displayed in the admin/accounts/account page


admin.site.register(Account, AccountAdmin)
