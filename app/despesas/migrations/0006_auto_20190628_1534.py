# Generated by Django 2.2.2 on 2019-06-28 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('despesas', '0005_auto_20190611_1939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='despesa',
            name='identificacao',
            field=models.CharField(help_text='Descrição da despesa.', max_length=250, verbose_name='Histórico'),
        ),
    ]
