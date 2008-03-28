from datetime import date, datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.xheaders import populate_xheaders
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _, ungettext
from django.views.generic.create_update import create_object, update_object, delete_object
from django.newforms import form_for_instance, form_for_model

from itkufs.common.decorators import limit_to_group, limit_to_owner, limit_to_admin
from itkufs.accounting.models import Group, Account
from itkufs.reports.models import *
from itkufs.reports.forms import *

@login_required
@limit_to_group
def show_list(request, group, list, is_admin=False):
    """Show list for printing"""

    if list.accounts.all().count():
        accounts = list.accounts.filter(group=group, active=True).select_related(depth=1)
    else:
        accounts = group.user_account_set.filter(active=True).select_related(depth=1)

    response = render_to_response('reports/list.html',
                              {
                                  'accounts': accounts,
                                  'group': group,
                                  'list': list,
                                  'is_admin': is_admin,
                              },
                              context_instance=RequestContext(request))
    populate_xheaders(request, response, List, list.id)
    return response

@login_required
@limit_to_admin
def edit_list(request, group, list=None, is_admin=False, type='new'):
    """Edit list"""
    if request.method == 'POST':
        data = request.POST
    else:
        data = None

    if type == 'new':
        columnforms = []
        listform = ListForm(data=data, group=group)
        for i in range(0,4): # Lock number of coloumns for new list
            columnforms.append( ColumnForm(data=data, prefix='new%s'%i))

    elif type == 'edit':
        if list is None:
            raise Http404

        listform = ListForm(data, instance=list, group=group)

        columnforms = []
        for c in list.column_set.all():
            columnforms.append( ColumnForm(data, instance=c, prefix=c.id) )

        for i in range(0,3):
            columnforms.append( ColumnForm(data, prefix='new%s'%i) )
    else:
        raise Exception('Unknown type for edit_list')

    if data and listform.is_valid():
        forms_ok = True
        for column in columnforms:
            if not column.is_valid():
                forms_ok = False
                break
        if forms_ok:
            list = listform.save(group=group)

            for column in columnforms:
                if column.cleaned_data['name'] and column.cleaned_data['width']:
                    column.save(list=list)
                elif column.instance.id:
                    column.instance.delete()

            return HttpResponseRedirect(reverse('view-list', args=(group.slug, list.slug)))

    return render_to_response('reports/list_form.html',
                              {
                                  'is_admin': is_admin,
                                  'group': group,
                                  'listform': listform,
                                  'columnforms': columnforms,
                              },
                              context_instance=RequestContext(request))

@login_required
@limit_to_group
def balance(request, group, is_admin=False):
    """Show balance sheet for the group"""

    # Balance sheet data struct
    accounts = {
        'as': [], 'as_sum': 0,
        'li': [], 'li_sum': 0,
        'eq': [], 'eq_sum': 0,
        'li_eq_sum': 0,
    }

    # Assets
    for account in group.account_set.filter(type=Account.ASSET_ACCOUNT):
        balance = account.user_balance()
        accounts['as'].append((account.name, balance))
        accounts['as_sum'] += balance

    # Liabilities
    for account in group.account_set.filter(type=Account.LIABILITY_ACCOUNT,
                                            owner__isnull=True):
        balance = account.user_balance()
        accounts['li'].append((account.name, balance))
        accounts['li_sum'] += balance

    # Accumulated member accounts liabilities
    member_balance_sum = 0
    for account in group.account_set.filter(type=Account.LIABILITY_ACCOUNT,
                                            owner__isnull=False):
        member_balance_sum += account.user_balance()
    accounts['li'].append((_('Member accounts'), member_balance_sum))
    accounts['li_sum'] += member_balance_sum

    # Equities
    for account in group.account_set.filter(type=Account.EQUITY_ACCOUNT):
        balance = account.user_balance()
        accounts['eq'].append((account.name, balance))
        accounts['eq_sum'] += balance

    # Total liabilities and equities
    accounts['li_eq_sum'] = accounts['li_sum'] + accounts['eq_sum']

    # Current year's net income
    curr_year_net_income = accounts['as_sum'] - accounts['li_eq_sum']
    accounts['eq'].append((_("Current year's net income"),
                           curr_year_net_income))
    accounts['eq_sum'] += curr_year_net_income
    accounts['li_eq_sum'] += curr_year_net_income

    return render_to_response('reports/balance.html',
                              {
                                  'is_admin': is_admin,
                                  'group': group,
                                  'today': date.today(),
                                  'accounts': accounts,
                              },
                              context_instance=RequestContext(request))

@login_required
@limit_to_group
def income(request, group, is_admin=False):
    """Show income statement for group"""

    # Balance sheet data struct
    accounts = {
        'in': [], 'in_sum': 0,
        'ex': [], 'ex_sum': 0,
        'in_ex_diff': 0,
    }

    # Incomes
    for account in group.account_set.filter(type=Account.INCOME_ACCOUNT):
        balance = account.user_balance()
        accounts['in'].append((account.name, balance))
        accounts['in_sum'] += balance

    # Expenses
    for account in group.account_set.filter(type=Account.EXPENSE_ACCOUNT):
        balance = account.user_balance()
        accounts['ex'].append((account.name, balance))
        accounts['ex_sum'] += balance

    # Net income
    accounts['in_ex_diff'] = accounts['in_sum'] - accounts['ex_sum']

    return render_to_response('reports/income.html',
                              {
                                  'is_admin': is_admin,
                                  'group': group,
                                  'today': date.today(),
                                  'accounts': accounts,
                              },
                              context_instance=RequestContext(request))

@login_required
@limit_to_admin
def settlement_summary(request, group, page='1', is_admin=False):
    """Show settlement summary"""

    pass # FIXME
