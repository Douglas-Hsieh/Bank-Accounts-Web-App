# Generated by Django 2.1.1 on 2018-09-18 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_account_isingoodstanding'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='isInGoodStanding',
        ),
    ]