from django.db import models  # Python objects that map to the database
from django.contrib.auth.models import Permission, User  # User models from Django Auth

from django.utils import timezone

from .exceptions import InsufficientFunds

# Create your models here.

# Models:
# Model represent database tables
# The fields of a models.Model correspond to columns of a SQL database table.

# Attributes:
# blank=True/False specifies whether it will render as required or not
# null=True means the database table column may contain null values
# null=False means the database table column may not contain null values
# on_delete=model.SET_NULL means when the model instance is deleted, we will implement this by setting the field to Null

# Choices:
# Create choices inside Model classes when you need the user to select static choices
# Choices are enforced by Django's form validation
# Default widget is a check box with these choices instead of text field

# Permissions:
# Permission models store information associating users/groups to permissions
# class Meta:
#     permissions = (
#         ("is_updating_own_account", "Update an Account that the User holds")
#     )


class Account(models.Model):
    """
    Each instance represent a User's bank account.
    """

    CHECKING = "Checking"
    SAVINGS = "Savings"
    ACCOUNT_TYPE_CHOICES = (
        (CHECKING, 'Checking'),  # Each inner tuple is of form: (value to be set in model, human readable name)
        (SAVINGS, 'Savings'),
    )

    UCU = 'UCU'
    CHASE = 'Chase'
    WELLS_FARGO = 'Wells Fargo'
    BANK_OF_AMERICA = 'Bank of America'
    BANK_CHOICES = (
        (UCU, 'UCU'),
        (CHASE, 'Chase'),
        (WELLS_FARGO, 'Wells Fargo'),
        (BANK_OF_AMERICA, 'Bank of America'),
    )

    account_type = models.CharField(max_length=200, default=None, choices=ACCOUNT_TYPE_CHOICES)
    creator = models.CharField(max_length=200, default=None)  # Account creator
    holder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Account holder is a site user
    balance = models.IntegerField(default=0)
    bank = models.CharField(max_length=200, default='UCU', null=True, choices=BANK_CHOICES)
    routing_number = models.IntegerField(null=True)

    def __str__(self):
        return self.account_type + ' Account ' + str(self.id)

    def deposit(self, amount):
        self.balance = self.balance + amount
        self.save()

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFunds()

        self.balance = self.balance - amount
        self.save()


class InternalTransferReceipt(models.Model):
    """
    Each instance is a set of information associated with a successful internal transfer.
    """

    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)  # User that made the transfer
    from_account = models.ForeignKey(to=Account, on_delete=models.SET_NULL, null=True,
                                     related_name='internaltransferreceipt_from_account')
    to_account = models.ForeignKey(to=Account, on_delete=models.SET_NULL, null=True,
                                   related_name='internaltransferreceipt_to_account')
    amount = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)  # date of transfer
    # comment = models.CharField(max_length=500)  # User comments on nature of transfer

    def __str__(self):
        return str(self.id)


class ExternalTransferReceipt(models.Model):
    """
    Each instance is a set of information associated with a successful external transfer.
    """
    payer = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True,
                              related_name='externaltransferreceipt_payer')
    payee = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True,
                              related_name='externaltransferreceipt_payee')
    from_account = models.ForeignKey(to=Account, on_delete=models.SET_NULL, null=True,
                                     related_name='externaltransferreceipt_from_account')
    to_account = models.ForeignKey(to=Account, on_delete=models.SET_NULL, null=True,
                                   related_name='externaltransferreceipt_to_account')
    amount = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)  # date of transfer
    comment = models.CharField(max_length=500)  # User comment on nature of transfer

    def __str__(self):
        return str(self.id)



