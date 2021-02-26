# Generated by Django 2.2 on 2019-04-05 15:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0028_auto_20190405_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientefaturas',
            name='valor_fatura',
            field=models.FloatField(blank=True, default=0, help_text='Valor total da fatura, observando-se os serviços e descosntos.', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Valor da fatura'),
        ),
        migrations.AlterField(
            model_name='clientefaturas',
            name='valor_servicos',
            field=models.FloatField(blank=True, default=0, help_text='Valor total dos serviços relacionados à fatura.', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Valor dos serviços'),
        ),
    ]