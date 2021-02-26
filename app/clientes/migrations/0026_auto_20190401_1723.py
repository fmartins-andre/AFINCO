# Generated by Django 2.1.7 on 2019-04-01 17:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0025_auto_20190328_1921'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clientefaturas',
            options={'ordering': ['-data_fatura', 'liquidado', 'cliente', '-data_pagamento'], 'verbose_name': 'Fatura de Serviços ao Cliente', 'verbose_name_plural': 'Faturas de Serviços aos Clientes'},
        ),
        migrations.AlterModelOptions(
            name='clienteservicos',
            options={'ordering': ['-data', 'contabilizar', 'liquidado', '-caixa', 'cliente', 'tipo_protocolo', 'protocolo', 'valor'], 'verbose_name': 'Serviço ao cliente', 'verbose_name_plural': 'Serviços prestados ao Clientes'},
        ),
    ]
