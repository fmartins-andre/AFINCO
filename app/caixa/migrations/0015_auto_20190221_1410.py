# Generated by Django 2.1.7 on 2019-02-21 17:10

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caixa', '0014_configuracaocaixa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configuracaocaixa',
            name='usuarios',
            field=models.ManyToManyField(help_text='Usuários aos quais se aplica a configuração de caixa.', to=settings.AUTH_USER_MODEL, verbose_name='Usuários'),
        ),
    ]
