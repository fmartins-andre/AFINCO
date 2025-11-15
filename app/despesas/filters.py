from django import forms
from django.utils.translation import gettext as _
from django.db.models import Q

import django_filters

from .models import CategoriaDespesa, Despesa


class DateInput(forms.DateInput):
    """Render input as html5 date input"""
    input_type = 'date'


class CustomDateRangeWidget(django_filters.widgets.RangeWidget):

    def __init__(self, widgets=None, from_attrs=None, to_attrs=None, attrs=None):
        widgets = (DateInput, DateInput)
        super(django_filters.widgets.RangeWidget, self).__init__(widgets, attrs)
        if from_attrs:
            self.widgets[0].attrs.update(from_attrs)
        if to_attrs:
            self.widgets[1].attrs.update(to_attrs)


class CustomNumberRangeWidget(django_filters.widgets.RangeWidget):

    def __init__(self, widgets=None, from_attrs=None, to_attrs=None, attrs=None):
        widgets = (forms.NumberInput, forms.NumberInput)
        super(django_filters.widgets.RangeWidget, self).__init__(widgets, attrs)
        if from_attrs:
            self.widgets[0].attrs.update(from_attrs)
        if to_attrs:
            self.widgets[1].attrs.update(to_attrs)


class CustomBooleanWidget(django_filters.widgets.BooleanWidget):

    def __init__(self, attrs=None):
        choices = (
            ('', _('------')),
            ('true', _('Sim')),
            ('false', _('Não')),
        )
        super(django_filters.widgets.BooleanWidget, self).__init__(attrs, choices)


class CategoriaDespesaFilter(django_filters.FilterSet):
    """Filtros para view"""
    ds = django_filters.CharFilter(
        field_name='identificacao',
        label='Descrição',
        help_text='Procura termo na descrição.',
        lookup_expr='icontains',
        widget=forms.TextInput(
            attrs={'class': 'form-control'},
        ),
    )
    at = django_filters.BooleanFilter(
        field_name='ativo',
        label='Ativo?',
        help_text='Categorias ativas ou não.',
        widget=CustomBooleanWidget(
            attrs={'class': 'form-control col-12'},
        ),
    )
    cc = django_filters.CharFilter(
        field_name='conta_credito',
        label='Conta Crédito',
        help_text='Procura por categorias com a conta indicada.',
        lookup_expr='icontains',
        widget=forms.NumberInput(
            attrs={'class': 'form-control'},
        ),
    )
    cd = django_filters.CharFilter(
        field_name='conta_debito',
        label='Conta Débito',
        help_text='Procura por categorias com a conta indicada.',
        lookup_expr='icontains',
        widget=forms.NumberInput(
            attrs={'class': 'form-control'},
        ),
    )
    cr = django_filters.CharFilter(
        field_name='codigo_rf',
        label='Código RFB',
        help_text='Procura por categorias com o código indicado.',
        lookup_expr='icontains',
        widget=forms.NumberInput(
            attrs={'class': 'form-control'},
        ),
    )

    class Meta:
        model = CategoriaDespesa
        fields = [
            'ds',  # descricao
            'at',  # ativo
            'cc',  # conta credito
            'cd',  # conta debito
            'cr',  # código rf
        ]


#
### DESPESAS

class DespesaFilter(django_filters.FilterSet):
    """Filtros para view"""
    ds = django_filters.CharFilter(
        field_name='identificacao__identificacao',
        label='Histórico',
        help_text='Procura termo no campo de histórico.',
        lookup_expr='icontains',
        widget=forms.TextInput(
            attrs={'class': 'form-control'},
        ),
    )
    dd = django_filters.DateFromToRangeFilter(
        field_name='data_despesa',
        label='Data entre:',
        help_text='Datas de início e fim, respectivamente. (Pode-se utilizar apenas um dos campos.)',
        widget=CustomDateRangeWidget(
            attrs={'class': 'webkit-no-spin form-control col-6'},
            to_attrs={'style': 'margin-left: -.41rem;'},
        ),
    )
    vl = django_filters.RangeFilter(
        field_name='valor',
        label='Valor entre:',
        help_text='Apresenta apenas os valores que estiverem entre o mínimo e o máximo indicados.',
        widget=CustomNumberRangeWidget(
            attrs={'class': 'form-control col-6'},
            from_attrs={'placeholder': 'Valor mínimo', },
            to_attrs={'placeholder': 'Valor máximo', 'style': 'margin-left: -.41rem;'},
        ),
    )
    ct = django_filters.CharFilter(
        method='filter_categoria_despesa',
        label='Categoria',
        help_text='Busca termo nos campos da categoria.',
        widget=forms.TextInput(
            attrs={'class': 'form-control'},
        ),
    )

    def filter_categoria_despesa(self, qs, name, value):
        return qs.filter(
            Q(categoria_despesa__identificacao__icontains=value) |
            Q(categoria_despesa__codigo_rf__icontains=value) |
            Q(categoria_despesa__conta_credito__icontains=value) |
            Q(categoria_despesa__conta_debito__icontains=value)
        )


    class Meta:
        model = CategoriaDespesa
        fields = [
            'ds',  # descricao
            'dd',  # data despesa
            'vl',  # valor
            'ct',  # categoria__identificacao
        ]
