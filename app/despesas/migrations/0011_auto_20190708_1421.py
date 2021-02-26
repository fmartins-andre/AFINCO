# Generated by Django 2.2.2 on 2019-07-08 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('despesas', '0010_auto_20190701_2043'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoriadespesa',
            name='relatorios',
            field=models.BooleanField(default=True, help_text='Indica se as despesas dessa categoria podem ser consideradas pelos relatórios.', verbose_name='Relatório?'),
        ),
        migrations.AddField(
            model_name='despesa',
            name='contabilizar_cofre',
            field=models.BooleanField(default=False, help_text='Indica se a despesa deve ser descontada do saldo do cofre, quando vinculada.', verbose_name='Contabilizar no Cofre?'),
        ),
    ]
