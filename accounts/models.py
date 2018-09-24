from django.db import models

# Create your models here.

# Attributes:
# blank=True/False specifies whether it will render as required or not
# null=True/False means the object can be null or empty in the DATABASE

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
    owner = models.CharField(max_length=200, default=None)
    balance = models.IntegerField(default=0)
    bank = models.CharField(max_length=200, default='UCU', null=True, choices=BANK_CHOICES)
    routing_number = models.IntegerField(null=True)

    def __str__(self):
        return str(self.id)
