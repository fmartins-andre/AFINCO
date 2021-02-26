# Generated by Django 2.1.7 on 2019-04-03 16:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0026_auto_20190401_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientefaturas',
            name='valor_descontos',
            field=models.FloatField(blank=True, default=0, help_text='Valor total dos descontos incidentes sobre a fatura, quando houver.', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Valor dos descontos'),
        ),
    ]
