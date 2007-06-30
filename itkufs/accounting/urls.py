from django.conf.urls.defaults import *
from itkufs.accounting.views import *
from itkufs.accounting.list_view import *

urlpatterns = patterns('',
    # Account list
    url(r'^$',
        account_list, name='account-list'),

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

    # Print lists
    url(r'^(?P<group>[0-9a-z_-]+)/list/$',
        list, name='list-select'),
    url(r'^(?P<group>[0-9a-z_-]+)/list/internal/$',
        list, {'list_type': 'internal'}, name='list-internal'),
    url(r'^(?P<group>[0-9a-z_-]+)/list/external/$',
        list, {'list_type': 'external'}, name='list-external'),

    url(r'(?P<account_group>[0-9a-z_-]+)/list/(?P<listtype>[0-9a-z]+)/pdf/$',
        generate_pdf, name='list-pdf'),
    

    # Admin: Account group summary
    url(r'^(?P<group>[0-9a-z_-]+)/$',
        group_summary, name='group-summary'),

    # Admin: Transactions
    # FIXME

    # Admin: Settlements
    # FIXME

    # Admin: Balance
    # FIXME
)
