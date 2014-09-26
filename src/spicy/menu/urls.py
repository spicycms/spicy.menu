from django.conf.urls import patterns, include, url


public_urls = patterns(
    'spicy.menu.views',
    url(r'^menu/(?P<slug>.+)/$', 'menu', name='menu'),
)


admin_urls = patterns(
    'spicy.menu.admin',

    url(r'^$', 'create', name='index'),
    url(r'^ajax_list/(?P<menu_slug>\S+)/$', 'menu_list_ajax', name='ajaxlist'),
    url(r'^create/$', 'create', name='create'),
    url(r'^(?P<menu_slug>[-_a-zA-Z0-9]+)/$',
        'menu_list_tree', name='edit-ajax'),
    url(r'^(?P<menu_slug>[-_a-zA-Z0-9]+)/preview/$',
        'preview', name='preview'),
    url(r'^(?P<menu_id>\d+)/delete/$', 'delete', name='delete'),



    url(r'^entries/add/$', 'entry_add', name='entry-add'),
    url(r'^entries/(?P<entry_id>\d+)/$',
        'entry_edit_ajax', name='entry-edit-ajax'),
    url(r'^entries/(?P<entry_id>\d+)/move/$', 'entry_move', name='entry-move'),
    url(r'^entries/(?P<entry_id>\d+)/copy/(?P<menu_id>\d+)/$',
        'entry_copy', name='entry-copy'),
    url(
        r'^entries/(?P<entry_id>\d+)/delete/$', 'entry_delete',
        name='entry-delete'),
)


urlpatterns = patterns(
    '',
    url(r'^admin/menu/', include(admin_urls, namespace='admin')),
    url(r'^', include(public_urls, namespace='public')),
)
