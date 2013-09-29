from django.conf.urls import patterns, include, url


public_urls = patterns(
    'spicy.menu.views',
    url(r'^menu/(?P<slug>.+)/$', 'menu', name='menu'),
)


admin_urls = patterns(
    'spicy.menu.admin',
    url(r'^$', 'menu_list', name='index'),
    url(r'^create/$', 'create', name='create'),
    url(r'^(?P<menu_id>\d+)/$', 'edit', name='edit'),
    url(r'^(?P<menu_id>\d+)/delete/$', 'delete', name='delete'),
    url(r'^entries/$', 'entry_list', name='entry-list'),
    url(r'^entries/add/$', 'entry_add', name='entry-add'),
    url(r'^entries/(?P<entry_id>\d+)/$', 'entry_edit', name='entry-edit'),
    url(
        r'^entries/(?P<entry_id>\d+)/delete/$', 'entry_delete',
        name='entry-delete'),
)


urlpatterns = patterns(
    '',
    url(r'^admin/menu/', include(admin_urls, namespace='admin')),
    url(r'^', include(public_urls, namespace='public')),
)
