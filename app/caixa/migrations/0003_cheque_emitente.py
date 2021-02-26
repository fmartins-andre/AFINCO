# Generated by Django 2.1.2 on 2018-11-06 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caixa', '0002_auto_20181029_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='cheque',
            name='emitente',
            field=models.CharField(blank=True, help_text='Identificação de quem emitiu o cheque.', max_length=200, null=True, verbose_name='Emitente'),
        ),
    ]