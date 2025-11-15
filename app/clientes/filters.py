# pylint: disable=missing-module-docstring,missing-class-docstring,bad-super-call
from django import forms
from django.utils.translation import gettext as _

import django_filters

from .models import ClienteServicos, ClienteFaturas


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


class ClienteServicosFilter(django_filters.FilterSet):
    """Filtros para view"""

    db = django_filters.DateFromToRangeFilter(
        field_name="data",
        label="Data entre:",
        help_text=(
            "Datas de início e fim, respectivamente. "
            "(Pode-se utilizar apenas um dos campos.)"
        ),
        widget=CustomDateRangeWidget(
            attrs={"class": "form-control col-6"},
            to_attrs={"style": "margin-left: -.41rem;"},
        ),
    )
    vb = django_filters.RangeFilter(
        field_name="valor",
        label="Valor entre:",
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
    cn = django_filters.CharFilter(
        field_name="cliente__nome",
        label="Cliente",
        help_text="Procura por clientes que tenham em seu nome o termo indicado.",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control"},
        ),
    )
    lq = django_filters.BooleanFilter(
        field_name="liquidado",
        label="Liquidado?",
        help_text="Serviços pagos.",
        widget=CustomBooleanWidget(
            attrs={"class": "form-control col-12"},
        ),
    )
    ct = django_filters.BooleanFilter(
        field_name="contabilizar",
        label="Contabilizar?",
        help_text="Serviços a contabilizar.",
        widget=CustomBooleanWidget(
            attrs={"class": "form-control col-12"},
        ),
    )
    pr = django_filters.CharFilter(
        field_name="protocolo",
        label="Protocolo",
        help_text="Procura por serviços com o protocolo indicado.",
        lookup_expr="icontains",
        widget=forms.NumberInput(
            attrs={"class": "form-control"},
        ),
    )

    class Meta:
        model = ClienteServicos
        fields = [
            "db",  # date_between
            "cn",  # cliente_nome
            "vb",  # valor_between
            "lq",  # liquidado
            "ct",  # contabilizar
            "pr",  # protocolo
        ]


class ClienteFaturasFilter(django_filters.FilterSet):
    fd = django_filters.DateFromToRangeFilter(
        field_name="data_fatura",
        label="Data da fatura entre:",
        help_text=(
            "Data da fatura entre início e fim , respectivamente. "
            "(Pode-se utilizar apenas um dos campos.)"
        ),
        widget=CustomDateRangeWidget(
            attrs={"class": "form-control col-6"},
            to_attrs={"style": "margin-left: -.41rem;"},
        ),
    )
    pg = django_filters.DateFromToRangeFilter(
        field_name="data_pagamento",
        label="Liquidado entre:",
        help_text=(
            "Liquidado entre início e fim , respectivamente. "
            "(Pode-se utilizar apenas um dos campos.)"
        ),
        widget=CustomDateRangeWidget(
            attrs={"class": "form-control col-6"},
            to_attrs={"style": "margin-left: -.41rem;"},
        ),
    )
    vb = django_filters.RangeFilter(
        field_name="valor_fatura",
        label="Valor entre:",
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
    cn = django_filters.CharFilter(
        field_name="cliente__nome",
        label="Cliente",
        help_text="Procura por clientes que tenham em seu nome o termo indicado.",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control"},
        ),
    )
    lq = django_filters.BooleanFilter(
        field_name="liquidado",
        label="Liquidado?",
        help_text="Serviços pagos.",
        widget=CustomBooleanWidget(
            attrs={"class": "form-control col-12 "},
        ),
    )

    class Meta:
        model = ClienteFaturas
        fields = [
            "fd",  # fatura_date_between
            "pg",  # pagamento_date_between
            "cn",  # cliente_nome
            "vb",  # valor_between
            "lq",  # liquidado
        ]


class ClientePagamentosFilter(django_filters.FilterSet):
    da = django_filters.DateFromToRangeFilter(
        field_name="data_add",
        label="Adicionado entre:",
        help_text=(
            "Data da inclusão entre início e fim , respectivamente. "
            "(Pode-se utilizar apenas um dos campos.)"
        ),
        widget=CustomDateRangeWidget(
            attrs={"class": "form-control col-6"},
            to_attrs={"style": "margin-left: -.41rem;"},
        ),
    )
    pg = django_filters.DateFromToRangeFilter(
        field_name="data_pagamento",
        label="Data do pagamento entre:",
        help_text=(
            "Data do pagamento entre início e fim , respectivamente. "
            "(Pode-se utilizar apenas um dos campos.)"
        ),
        widget=CustomDateRangeWidget(
            attrs={"class": "form-control col-6"},
            to_attrs={"style": "margin-left: -.41rem;"},
        ),
    )
    vb = django_filters.RangeFilter(
        field_name="valor",
        label="Valor entre:",
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
    cn = django_filters.CharFilter(
        field_name="cliente__nome",
        label="Cliente",
        help_text="Procura por clientes que tenham em seu nome o termo indicado.",
        lookup_expr="icontains",
        widget=forms.TextInput(
            attrs={"class": "form-control"},
        ),
    )

    class Meta:
        model = ClienteFaturas
        fields = [
            "da",  # pagamento_date_add_between
            "pg",  # pagamento_date_between
            "cn",  # cliente_nome
            "vb",  # valor_between
        ]
