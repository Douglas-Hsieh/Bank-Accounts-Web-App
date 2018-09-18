from django.db import models

# Create your models here.

# Attributes:
# blank=True/False specifies whether it will render as required or not
# null=True/False means the object can be null or empty in the DATABASE


class Account(models.Model):
    type = models.CharField(max_length=200, default=None)
    owner = models.CharField(max_length=200, default=None)
    balance = models.IntegerField(default=0)
    bank = models.CharField(max_length=200, default='UCU', null=True)
    routing_number = models.IntegerField(null=True)

    def __str__(self):
        return str(self.id)

