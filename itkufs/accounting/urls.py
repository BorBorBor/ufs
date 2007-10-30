from django.conf.urls.defaults import *
from itkufs.accounting.views import *

urlpatterns = patterns('',
    # Login
    url(r'login/$',
        login_user, name='login'),

    # Account list
    url(r'^$',
        group_list, name='group-list'),

    # My account
    url(r'^(?P<group>[0-9a-z_-]+)/a/(?P<account>[0-9a-z_-]+)/$',
        account_summary, name='account-summary'),
    url(r'^(?P<group>[0-9a-z_-]+)/a/(?P<account>[0-9a-z_-]+)/(?P<page>\d+)/$',
        account_summary, name='account-summary-page'),
    url(r'^(?P<group>[0-9a-z_-]+)/a/(?P<account>[0-9a-z_-]+)/deposit/$',
        transfer, {'transfer_type': 'deposit'}, name='account-deposit'),
    url(r'^(?P<group>[0-9a-z_-]+)/a/(?P<account>[0-9a-z_-]+)/withdraw/$',
        transfer, {'transfer_type': 'withdraw'}, name='account-withdraw'),
    url(r'^(?P<group>[0-9a-z_-]+)/a/(?P<account>[0-9a-z_-]+)/transfer/$',
        transfer, {'transfer_type': 'transfer'}, name='account-transfer'),

    # My group
    url(r'^(?P<group>[0-9a-z_-]+)/$',
        group_summary, name='group-summary'),
    url(r'^(?P<group>[0-9a-z_-]+)/list/internal/html/$',
        generate_html, {'list_type': 'internal'}, name='list-html'),

    # Admin: Transactions
    url(r'^(?P<group>[0-9a-z_-]+)/approve/$',
        approve, name='approve-transactions'),
    url(r'^(?P<group>[0-9a-z_-]+)/approve/(?P<page>\d+)/$',
        approve, name='approve-transactions-page'),
    url(r'^(?P<group>[0-9a-z_-]+)/register/$',
        transfer, {'transfer_type': 'register'}, name='register-transactions'),

    # Admin: Settlements
    url(r'^(?P<group>[0-9a-z_-]+)/settlement/$',
        settlement_summary, name='settlement-summary'),
    url(r'^(?P<group>[0-9a-z_-]+)/settlement/(?P<page>\d+)/$',
        settlement_summary, name='settlement-summary-page'),

    # Admin: Balance
    url(r'^(?P<group>[0-9a-z_-]+)/balance/$',
        balance, name='balance'),
)
