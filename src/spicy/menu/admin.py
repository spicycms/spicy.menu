# coding=utf-8
from django import http
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from spicy.core.admin.conf import AdminAppBase, AdminLink, Perms
from spicy.core.profile.decorators import is_staff
from spicy.core.admin import defaults as admin_defaults
from spicy.core.siteskin.decorators import render_to
from spicy.utils import NavigationFilter
from . import forms, models


class AdminApp(AdminAppBase):
    name = 'menu'
    label = _('Menu')
    order_number = 3

    menu_items = (
        AdminLink('menu:admin:create', _('Create menu')),
        AdminLink('menu:admin:index', _('All menu')),
        AdminLink('menu:admin:entry-add', _('Create menu entry')),
        AdminLink('menu:admin:entries-list', _('Menu entries')),
    )

    create = AdminLink('menu:admin:create', _('Create menu'),)

    perms = Perms(view=[],  write=[], manage=[])

    @render_to('menu.html', use_admin=True)
    def menu(self, request, *args, **kwargs):
        return dict(app=self, *args, **kwargs)

    @render_to('dashboard.html', use_admin=True)
    def dashboard(self, request, *args, **kwargs):
        return dict(app=self, *args, **kwargs)


@is_staff(required_perms='menu.change_menu')
@render_to('list.html', use_admin=True)
def menu_list(request):
    nav = NavigationFilter(request)
    paginator = nav.get_queryset_with_paginator(models.Menu)
    objects_list = paginator.current_page.object_list
    return {'paginator': paginator, 'objects_list': objects_list, 'nav': nav}


@is_staff(required_perms='menu.add_menu')
@render_to('create.html', use_admin=True)
def create(request):
    if request.method == 'POST':
        form = forms.MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(reverse(
                'menu:admin:index'))
    else:
        form = forms.MenuForm()
    return {'form': form}


@is_staff(required_perms='menu.change_menu')
@render_to('edit.html', use_admin=True)
def edit(request, menu_id):
    menu = get_object_or_404(models.Menu, pk=menu_id)
    if request.method == 'POST':
        form = forms.MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(reverse(
                'menu:admin:index'))
    else:
        form = forms.MenuForm(instance=menu)
    return {
        'form': form, 'add_url_name': _('Menu entry'),
        'add_url': (
            reverse('menu:admin:entry-add') + u'?menu=' + unicode(menu.pk))}


@is_staff(required_perms='menu.delete_menu')
@render_to('delete.html', use_admin=True)
def delete(request, menu_id):
    message = ''
    status = 'ok'

    menu = get_object_or_404(models.MenuEntry, pk=menu_id)

    if request.method == 'POST' and 'confirm' in request.POST:
        menu.delete()
        return http.HttpResponseRedirect(
            reverse('menu:admin:index'))

    return dict(message=unicode(message), status=status, instance=menu)


@is_staff(required_perms='menu.change_menu')
@render_to('list_entry.html', use_admin=True)
def entry_list(request):
    nav = NavigationFilter(request)
    paginator = nav.get_queryset_with_paginator(
        models.MenuEntry, obj_per_page=admin_defaults.ADMIN_OBJECTS_PER_PAGE)
    objects_list = paginator.current_page.object_list
    return {
        'paginator': paginator, 'objects_list': objects_list, 'nav': nav,
        'edit_url': 'menu:admin:entry-edit'}


@is_staff(required_perms='menu.add_menuentry')
@render_to('create.html', use_admin=True)
def entry_add(request):
    if request.method == 'POST':
        form = forms.EntryForm(request.POST)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(reverse(
                'menu:admin:entry-list'))
    else:
        form = forms.EntryForm(
            initial={
                'menu': request.GET.get('menu'),
                'parent': request.GET.get('parent')})
    return {'form': form}


@is_staff(required_perms='menu.change_menuentry')
@render_to('edit.html', use_admin=True)
def entry_edit(request, entry_id):
    entry = get_object_or_404(models.MenuEntry, pk=entry_id)
    if request.method == 'POST':
        form = forms.EntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(reverse(
                'menu:admin:entry-list'))
    else:
        form = forms.EntryForm(instance=entry)
    return {
        'form': form, 'add_url_name': _('Add sub entry'),
        'add_url': u'{url}?menu={menu}&parent={parent}'.format(
            url=reverse('menu:admin:entry-add'), menu=entry.menu_id,
            parent=entry_id)}


@is_staff(required_perms='menu.delete_menuentry')
@render_to('delete.html', use_admin=True)
def entry_delete(request, entry_id):
    message = ''
    status = 'ok'

    entry = get_object_or_404(models.MenuEntry, pk=entry_id)

    if request.method == 'POST':
        if 'confirm' in request.POST:
            entry.delete()
            return http.HttpResponseRedirect(
                reverse('menu:admin:index'))

    return dict(message=unicode(message), status=status, instance=entry)
