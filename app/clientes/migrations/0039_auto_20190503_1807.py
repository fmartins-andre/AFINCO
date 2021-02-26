# Generated by Django 2.2 on 2019-05-03 18:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0038_auto_20190502_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='saldo_faturado',
            field=models.FloatField(blank=True, default=0, help_text='Saldo entre receitas e despesas das faturas.', null=True, verbose_name='Saldo Faturado'),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='saldo',
            field=models.FloatField(blank=True, default=0, help_text='Saldo disponível na conta do cliente.', null=True, verbose_name='Saldo'),
        ),
    ]