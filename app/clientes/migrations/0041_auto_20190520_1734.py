# Generated by Django 2.2.1 on 2019-05-20 17:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0040_cliente_verifica_saldo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clienteservicos',
            name='data',
            field=models.DateField(default=django.utils.timezone.now, help_text='Data em que foi prestado o serviço.', verbose_name='Data'),
        ),
    ]
