from django.db import models  # Python objects that map to the database
from django.contrib.auth.models import User  # User models from Django Auth

# Create your models here.

# Attributes:
# blank=True/False specifies whether it will render as required or not
# null=True means the database table column may contain null values
# null=False means the database table column may not contain null values
# on_delete=model.SET_NULL means when the model instance is deleted, we will implement this by setting the field to Null

# Choices:
# Create choices inside Model classes when you need the user to select static choices
# Choices are enforced by Django's form validation
# Default widget is a check box with these choices instead of text field


class Account(models.Model):

    CHECKING = "Checking"
    SAVINGS = "Savings"
    TYPE_CHOICES = (
        (CHECKING, 'Checking'),  # Each inner tuple is of form: (value to be set in model, human readable name)
        (SAVINGS, 'Savings'),
    )

    UCU = 'UCU'
    CHASE = 'Chase'
    WELLS_FARGO = 'Wells Fargo'
    BANK_CHOICES = (
        (UCU, 'UCU'),
        (CHASE, 'Chase'),
        (WELLS_FARGO, 'Wells Fargo'),
    )

    type = models.CharField(max_length=200, default=None, choices=TYPE_CHOICES)
    creator = models.CharField(max_length=200, default=None)  # Account creator
    holder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Account holder is a site user
    balance = models.IntegerField(default=0)
    bank = models.CharField(max_length=200, default='UCU', null=True, choices=BANK_CHOICES)
    routing_number = models.IntegerField(null=True)

    def __str__(self):
        return str(self.id)
