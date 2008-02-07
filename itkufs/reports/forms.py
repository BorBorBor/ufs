from django import newforms as forms
from django.template.defaultfilters import slugify
from django.newforms.util import ValidationError

from itkufs.reports.models import *
from itkufs.common.forms import CustomModelForm

class ListForm(CustomModelForm):
    class Meta:
        model = List
        exclude = ('slug', 'group')

    def save(self, group=None, **kwargs):
        original_commit = kwargs['commit']
        kwargs['commit'] = False
        list = super(ListForm, self).save(**kwargs)

        if not list.slug:
            list.slug = slugify(list.name)
        if group:
            list.group = group

        if original_commit:
            list.save()
        return list

class ColumnForm(CustomModelForm):
    class Meta:
        model = ListColumn
        fields = ('name', 'width')

    def clean(self):
        test = self.cleaned_data
        if 'width' not in self.cleaned_data and 'name' not in self.cleaned_data:
            del self._errors['width']
            del self._errors['name']

        return self.cleaned_data

    def save(self, list=None, **kwargs):
        original_commit = kwargs['commit']
        kwargs['commit'] = False
        column = super(ColumnForm, self).save(**kwargs)

        if list:
           column.group = group

        if original_commit:
            column.save()
        return column
