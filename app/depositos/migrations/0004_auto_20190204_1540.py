# Generated by Django 2.1.5 on 2019-02-04 17:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('depositos', '0003_auto_20190118_1522'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='depositos',
            options={'ordering': ['-data_deposito', 'identificacao', 'valor'], 'verbose_name': 'Depósito Bancário', 'verbose_name_plural': 'Controle de Depósitos Bancários'},
        ),
    ]
