# Generated by Django 2.2.2 on 2019-06-11 19:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('despesas', '0003_auto_20190611_1723'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoriadespesa',
            options={'ordering': ['-ativo', 'identificacao', 'codigo_rf'], 'verbose_name': 'Categoria de Despesa', 'verbose_name_plural': 'Categorias de Despesas'},
        ),
    ]