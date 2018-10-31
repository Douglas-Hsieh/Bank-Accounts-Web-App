# Create Django Form objects here

from django import forms
from .models import Account

# Django Forms have automatic validation dependent on fields

# forms.Form allows for customization of forms
# forms.ModelForm has fields based upon a Model and allows for tweaking


class AccountForm(forms.ModelForm):  # a form associated with the database (via a model)
    """
    Form for creating an Account
    """
    class Meta:
        model = Account  # Database table this form is associated with
        fields = [  # Fields that this form will have. These fields are associated with the model fields.
            'account_type',
            'creator',
            'holder',
            'balance',
            'bank',
            'routing_number',
        ]


class AccountUpdateForm(forms.ModelForm):
    """
    Form for updating an Account
    """
    class Meta:
        model = Account
        fields = [
            'account_type'
        ]


class InternalTransferForm(forms.Form):
    """
    Form for making an internal transfer between Accounts
    """
    from_account = forms.IntegerField()
    to_account = forms.IntegerField()
    balance = forms.IntegerField()

