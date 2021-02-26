# Generated by Django 2.1.5 on 2019-01-23 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0004_clienteservicos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clienteservicos',
            name='tipo_protocolo',
            field=models.CharField(choices=[(None, '-------'), ('CE', 'Certidão'), ('RE', 'Registro'), ('EX', 'Exame e Cálculo')], default='CE', help_text='Tipo do protocolo do register', max_length=2, null=True, verbose_name='Tipo de protocolo'),
        ),
    ]
