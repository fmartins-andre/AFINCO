# Generated by Django 2.1.5 on 2019-01-23 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0008_auto_20190123_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='clienteservicos',
            name='contabilizar',
            field=models.BooleanField(default=True, help_text='Indica se o serviço deve ser considerado para fins contábeis.', verbose_name='Contabilizar?'),
        ),
    ]
