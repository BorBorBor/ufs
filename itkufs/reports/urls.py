from django.conf.urls import *

from itkufs.reports.views import *

urlpatterns = patterns('',
    ### Lists
    url(r'^(?P<group>[0-9a-z_-]+)/list/new/$',
        new_edit_list, name='new-list'),
    url(r'^(?P<group>[0-9a-z_-]+)/list/(?P<list>[0-9a-z_-]+)/$',
        view_list, name='view-list'),
    url(r'^(?P<group>[0-9a-z_-]+)/list/(?P<list>[0-9a-z_-]+)/preview/$',
        view_list_preview, name='view-list-preview'),
    url(r'^(?P<group>[0-9a-z_-]+)/list/(?P<list>[0-9a-z_-]+)/edit/$',
        new_edit_list, name='edit-list'),
    url(r'^(?P<group>[0-9a-z_-]+)/list/(?P<list>[0-9a-z_-]+)/delete/$',
        delete_list, name='delete-list'),
    url(r'^(?P<group>[0-9a-z_-]+)/list/(?P<list>[0-9a-z_-]+)/transaction/$',
        transaction_from_list, name='transaction-from-list'),

    ### Statements
    url(r'^(?P<group>[0-9a-z_-]+)/balance/$',
        balance, name='balance'),
    url(r'^(?P<group>[0-9a-z_-]+)/income/$',
        income, name='income'),
)
