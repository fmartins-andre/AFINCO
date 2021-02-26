# Generated by Django 2.1.5 on 2019-01-23 12:36

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('caixa', '0011_auto_20181205_1508'),
        ('clientes', '0003_auto_20190123_0917'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClienteServicos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(help_text='Data em que foi prestado o serviço.', verbose_name='Data')),
                ('tipo_protocolo', models.CharField(choices=[('CE', 'Certidão'), ('RE', 'Registro'), ('EX', 'Exame e Cálculo')], default='CE', help_text='Tipo do protocolo do register', max_length=2, null=True, verbose_name='Tipo de protocolo')),
                ('protocolo', models.PositiveIntegerField(blank=True, help_text='Protocolo do serviço prestado no register.', null=True, validators=[django.core.validators.MinValueValidator(10000), django.core.validators.MaxValueValidator(999999)], verbose_name='Protocolo')),
                ('valor', models.PositiveIntegerField(help_text='Valor do serviço prestado.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Valor')),
                ('liquidado', models.BooleanField(default=False, help_text='Indica se o serviço já foi liquidado/pago.', verbose_name='Liquidado?')),
                ('caixa', models.ForeignKey(blank=True, default=None, editable=False, help_text='Indica em que fechamento de caixa foi realizado o serviço.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='caixa.FechamentoCaixa', verbose_name='Fechamento de Caixa')),
                ('cliente', models.ForeignKey(help_text='Cliente ao qual foi prestado o serviço.', on_delete=django.db.models.deletion.PROTECT, to='clientes.Cliente', verbose_name='Cliente')),
            ],
            options={
                'verbose_name': 'Serviço',
                'verbose_name_plural': 'Serviços prestados ao clientes',
                'ordering': ['liquidado', '-data', 'cliente', 'tipo_protocolo', 'protocolo', 'valor'],
            },
        ),
    ]