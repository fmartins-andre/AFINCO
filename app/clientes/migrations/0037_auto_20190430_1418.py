# Generated by Django 2.2 on 2019-04-30 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0036_auto_20190429_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientepagamentos',
            name='forma_pagamento',
            field=models.CharField(choices=[('DP', 'Depósito'), ('DI', 'Dinheiro'), ('CQ', 'Cheque')], default='DI', max_length=2, verbose_name='Forma de pagamento'),
        ),
    ]
