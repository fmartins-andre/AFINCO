# pylint: disable=missing-module-docstring,missing-class-docstring,bad-super-call
from django import forms
from django.utils.translation import gettext as _
from django.db.models import Q

import django_filters

from .models import Depositos


class DateInput(forms.DateInput):
    """Render input as html5 date input"""

    input_type = "date"


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
            ("", _("------")),
            ("true", _("Sim")),
            ("false", _("Não")),
        )
        super(django_filters.widgets.BooleanWidget, self).__init__(attrs, choices)


class DepositosFilter(django_filters.FilterSet):
    """Filtros para view"""

    data_deposito = django_filters.DateFromToRangeFilter(
        field_name="data_deposito",
        label="Data",
        help_text=(
            "Datas de início e fim, respectivamente."
            "(Pode-se utilizar apenas um dos campos.)"
        ),
        widget=CustomDateRangeWidget(
            attrs={"class": "form-control col-6"},
            to_attrs={"style": "margin-left: -.41rem;"},
        ),
    )
    valor = django_filters.RangeFilter(
        field_name="valor",
        label="Valor",
        help_text="Apresenta apenas os valores que estiverem entre o mínimo e o máximo indicados.",
        widget=CustomNumberRangeWidget(
            attrs={"class": "form-control col-6"},
            from_attrs={
                "placeholder": "Valor mínimo",
                "step": "any",
            },
            to_attrs={
                "placeholder": "Valor máximo",
                "step": "any",
                "style": "margin-left: -.41rem;",
            },
        ),
    )
    identificacao = django_filters.CharFilter(
        method="filter_depositos_identificacao",
        label="Identificação",
        help_text="Procura termo na identificação e anotações do depósito.",
        widget=forms.TextInput(
            attrs={"class": "form-control"},
        ),
    )
    consolidado = django_filters.BooleanFilter(
        field_name="consolidado",
        label="Consolidado?",
        widget=CustomBooleanWidget(
            attrs={"class": "form-control col-12"},
        ),
    )
    ordering = django_filters.OrderingFilter(
        label="Ordenação",
        fields=(
            ("valor", "valor"),
            ("data_deposito", "data"),
            ("identificacao", "identificacao"),
        ),
        field_labels={
            "valor": "Valor",
            "data_deposito": "Data",
            "identificacao": "Identificação",
        },
    )

    def filter_depositos_identificacao(  # pylint: disable=no-self-use
        self, qs, name, value  # pylint: disable=unused-argument
    ):
        """Filtra os depósitos pelos campos identificação e observações em conjunto."""
        return qs.filter(
            Q(identificacao__icontains=value) | Q(observacoes__icontains=value)
        )

    class Meta:
        model = Depositos
        fields = [
            "data_deposito",
            "valor",
            "identificacao",
            "consolidado",
            "ordering",
        ]
