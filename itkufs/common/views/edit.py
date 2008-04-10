import os

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from itkufs.common.decorators import limit_to_admin
from itkufs.common.forms import GroupForm, AccountForm
from itkufs.accounting.models import Group, Account

@login_required
@limit_to_admin
def edit_group(request, group, is_admin=False):
    """Edit group properties"""

    old_logo = group.get_logo_filename()

    if request.method == 'POST':
        form = GroupForm(data=request.POST, files=request.FILES, instance=group)

        if form.is_valid():
            form.save()

            if old_logo and old_logo != group.get_logo_filename():
                os.remove(old_logo)
            elif 'delete_logo' in form.cleaned_data and old_logo:
                os.remove(group.get_logo_filename())
                group.logo = ''
                group.save()

            request.user.message_set.create(
                message=_('Group successfully updated'))

            return HttpResponseRedirect(reverse('group-summary',
                args=(group.slug,)))
    else:
        form = GroupForm(instance=group)

    return render_to_response('common/group_form.html',
        {
            'is_admin': is_admin,
            'group': group,
            'form': form,
        },
        context_instance=RequestContext(request))

@login_required
@limit_to_admin
def new_edit_account(request, group, account=None,
    is_admin=False, is_owner=False):
    """Create account or edit account properties"""

    if request.method == 'POST':
        if account is not None:
            form = AccountForm(instance=account, data=request.POST)
        else:
            form = AccountForm(data=request.POST)

        if form.is_valid():
            if account is not None:
                form.save()
                request.user.message_set.create(
                    message=_('Account successfully updated'))
            else:
                account = form.save(group=group)
                request.user.message_set.create(
                    message=_('Account successfully created'))
            return HttpResponseRedirect(reverse('account-summary',
                args=(group.slug, account.slug)))
    else:
        if account is not None:
            form = AccountForm(instance=account)
        else:
            form = AccountForm()

    return render_to_response('common/account_form.html',
        {
            'is_admin': is_admin,
            'group': group,
            'is_owner': is_owner,
            'account': account,
            'form': form,
        },
        context_instance=RequestContext(request))

