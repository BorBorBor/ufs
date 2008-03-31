from django import newforms as forms
from django.newforms.util import ValidationError
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

from itkufs.accounting.models import *
from itkufs.common.forms import CustomModelForm, CustomForm

class AccountForm(CustomModelForm):
    class Meta:
        model = Account
        exclude = ('slug', 'group')

    def save(self, group=None, **kwargs):
        original_commit = kwargs.pop('commit', True)
        kwargs['commit'] = False
        account = super(AccountForm, self).save(**kwargs)

        if not account.slug:
            account.slug = slugify(account.name)
        if group:
            account.group = group

        if original_commit:
            account.save()
        return account


class GroupForm(CustomModelForm):
    delete_logo = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        if 'instance' not in kwargs or kwargs['instance'].logo == '':
            del self.fields['delete_logo']

    class Meta:
        model = Group
        exclude = ('slug',)

    def save(self, **kwargs):
        original_commit = kwargs.pop('commit', True)
        kwargs['commit'] = False
        group = super(GroupForm, self).save(**kwargs)

        if not group.slug:
            group.slug = slugify(group.name)

        kwargs['commit'] = original_commit
        return super(GroupForm, self).save(**kwargs)


class TransactionSettlementForm(CustomModelForm):
    details = forms.CharField(label=_('Details'), required=False,
        widget=forms.widgets.Textarea(attrs={'rows': 2}))

    class Meta:
        model = Transaction
        fields = ('settlement',)


class SettlementForm(CustomModelForm):
    class Meta:
        model = Settlement
        exclude = ['group']


class ChangeTransactionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        choices = kwargs.pop('choices', (('',''),))
        label = kwargs.pop('label', True)
        super(forms.Form, self).__init__(*args, **kwargs)

        if not label:
            self.fields['change_to'].label = ''
        self.fields['change_to'].widget = forms.Select(choices=choices)

    change_to = forms.CharField(max_length=3, required=False)


class EntryForm(CustomForm):
    debit = forms.DecimalField(min_value=0, required=False, widget=forms.TextInput(attrs={'size': 4, 'class': 'number'}))
    credit = forms.DecimalField(min_value=0, required=False, widget=forms.TextInput(attrs={'size': 4, 'class': 'number'}))


class DepositWithdrawForm(forms.Form):
    amount = forms.DecimalField(label=_('Amount'), required=True, min_value=0)
    details = forms.CharField(label=_('Details'), required=False,
        widget=forms.widgets.Textarea(attrs={'rows': 2}))


class TransferForm(DepositWithdrawForm):
    credit_account = forms.ChoiceField(label=_('To'), required=True)

    def __init__(self, *args, **kwargs):
        account = kwargs.pop('account')

        super(DepositWithdrawForm, self).__init__(*args, **kwargs)

        if account:
            choices = []

            for a in account.group.user_account_set:
                if a != account:
                    choices.append((a.id, a.name))

            self.fields['credit_account'].choices = choices

class RejectTransactionForm(forms.Form):
    reason = forms.CharField(label=_('Reason'),
        widget=forms.widgets.Textarea(attrs={'rows': 2}), required=True)
