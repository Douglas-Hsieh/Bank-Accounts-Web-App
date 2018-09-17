from django.db import models

# Create your models here.


class Account(models.Model):
    type = models.CharField(max_length=200, default=None)
    owner = models.CharField(max_length=200, default=None)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)
