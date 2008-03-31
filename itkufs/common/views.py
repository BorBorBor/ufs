from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _, ungettext

from itkufs.accounting.models import Group, Account

def login_user(request):
    """Login user"""

    if not request.user.is_authenticated():
        user = authenticate(request=request)
        if user is not None:
            login(request, user)
        else:
            return HttpResponseForbidden(_('Login failed'))

    try:
        # Redirect to one of the user's accounts
        account = request.user.account_set.all()[0]
        url = reverse('account-summary',
                      kwargs={'group': account.group.slug,
                              'account': account.slug})
        return HttpResponseRedirect(url)
    except IndexError:
        pass

    # Tell the user he has a user, but not an account
    return render_to_response('common/no_account.html',
                              context_instance=RequestContext(request))

@login_required
def account_switch(request, is_admin=False):
    """Switch to account summary for the selected account"""

    if request.method != 'POST':
        raise Http404
    group_slug = request.POST['group']
    account = get_object_or_404(Account, owner=request.user,
        group__slug=group_slug)
    return HttpResponseRedirect(reverse('account-summary',
        kwargs={
            'group': account.group.slug,
            'account': account.slug,
        }))

@login_required
def static_page(request, template, is_admin=False):
    return render_to_response(template,
                              {
                                  'is_admin': is_admin,
                              },
                              context_instance=RequestContext(request))

