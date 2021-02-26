# Generated by Django 2.2.2 on 2019-09-10 20:06

import api_cartoes.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bandeiras',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(help_text='Nome da bandeira.', max_length=50, unique=True, verbose_name='Nome')),
                ('usar_debito', models.BooleanField(default=True, help_text='Indica se a bandeira poderá utilizar a modalidade de débito.', verbose_name='Usar débito')),
                ('usar_credito', models.BooleanField(default=True, help_text='Indica se a bandeira poderá utilizar a modalidade de crédito.', verbose_name='Usar crédito')),
                ('taxa_debito', models.DecimalField(blank=True, decimal_places=3, default=None, help_text='Taxa a para pagamentos a débito.', max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Taxa a débito')),
                ('taxa_credito_avista', models.DecimalField(blank=True, decimal_places=3, default=None, help_text='Taxa para pagamentos a crédito a vista.', max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Taxa a crédito a vista')),
                ('parcelar', models.BooleanField(default=False, help_text='Indica se será habilitada a opção de pagamento parcelado a crédito.', verbose_name='Permitir parcelamento a crédito')),
                ('taxa_6meses', models.BooleanField(default=False, help_text='Converte as taxas de crédito parcelado para taxas fixas para "até" e "acima de" 6 parcelas, respectivamente.', verbose_name='Modo 6/6')),
                ('parcelamento', models.SmallIntegerField(blank=True, default=None, help_text='Quantidade de parcelas permitidas para crédito.', null=True, validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(12)], verbose_name='Quantidade de parcelas')),
                ('taxa_credito_parcelado', models.DecimalField(blank=True, decimal_places=3, default=None, help_text='Taxa para pagamentos a crédito parcelado.', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Taxa a crédito parcelado')),
                ('taxa_credito_parcelado_porparcela', models.DecimalField(blank=True, decimal_places=3, default=None, help_text='Taxa a incidir sobre o número de parcelas do pagamento a crédito.', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Taxa a crédito parcelado, por parcela')),
                ('ativo', models.BooleanField(default=True, help_text='Indica se a bandeira está ou não habilitada para uso.', verbose_name='Habilitar')),
            ],
            options={
                'verbose_name': 'Bandeira',
                'verbose_name_plural': 'Bandeiras',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='Configuracoes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(default=api_cartoes.models.random_uuid_str, help_text='Nome dado à configuração.', max_length=50, unique=True, verbose_name='Nome')),
                ('precedencia', models.PositiveIntegerField(default=api_cartoes.models.random_number, help_text='Importância da configuração. Quanto maior o número, menor a precedência.', unique=True, verbose_name='Precedência')),
                ('valor_custa_register', models.DecimalField(decimal_places=2, help_text='Valor da custa utilizada no register.', max_digits=7, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Valor da custa')),
                ('taxa_credito', models.DecimalField(decimal_places=3, help_text='Taxa padrão a crédito.', max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Taxa a crédito')),
                ('taxa_debito', models.DecimalField(decimal_places=3, help_text='Taxa padrão a débito.', max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Taxa a débito')),
            ],
            options={
                'verbose_name': 'Configuração',
                'verbose_name_plural': 'Configurações',
            },
        ),
    ]