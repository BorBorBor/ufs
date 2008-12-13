from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.forms.models import ModelForm
from django.forms.forms import Form

from itkufs.reports.models import *

class ListForm(ModelForm):
    class Meta:
        model = List
        exclude = ('slug', 'group')

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group')
        super(ListForm, self).__init__(*args, **kwargs)

        self.fields['accounts'].choices = [(a.id, a.name) for a in group.user_account_set]

    def clean(self):
        account_width = self.cleaned_data['account_width']
        short_name_width = self.cleaned_data['short_name_width']

        if account_width == 0 and short_name_width == 0:
            fields = {
                'field1': self.fields['account_width'].label,
                'field2': self.fields['short_name_width'].label
            }

            raise forms.ValidationError(
                _(u'"%(field1)s" or "%(field2)s" must be greater than zero') % fields)
        return self.cleaned_data

    def save(self, group=None, **kwargs):
        original_commit = kwargs.pop('commit', True)

        kwargs['commit'] = False
        list = super(ListForm, self).save(**kwargs)

        if not list.slug:
            list.slug = slugify(list.name)
        if group:
            list.group = group

        if original_commit:
            list.save()
            list.accounts = self.cleaned_data['accounts']

        return list

class ColumnForm(ModelForm):
    name = forms.CharField(max_length=100, required=False)
    width = forms.IntegerField(min_value=0, required=False, widget=forms.TextInput(attrs={'size': 4, 'class': 'number'}))

    class Meta:
        model = ListColumn
        fields = ('name', 'width')

    def save(self, list=None, **kwargs):
        original_commit = kwargs.pop('commit', True)
        kwargs['commit'] = False
        column = super(ColumnForm, self).save(**kwargs)

        if list:
           column.list = list

        if original_commit:
            column.save()
        return column
