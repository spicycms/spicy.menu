# coding=utf-8
from django import http
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson
from spicy.core.admin.conf import AdminAppBase, AdminLink
from spicy.core.profile.decorators import is_staff
from spicy.core.siteskin.decorators import render_to, ajax_request
from django.template.response import TemplateResponse
from . import forms, models


def path_with_port(request):

    try:

        # if request.META.get('SERVER_PORT') and request.META.get('SERVER_PORT')\
        #         != '80':
        #     return 'http://' + request.get_host() + ':'\
        #         + request.META['SERVER_PORT'] + request.path
        # else:
        if request.is_secure():
            return 'https://' + request.get_host() + request.path
        else:
            return 'http://' + request.get_host() + request.path
    except:
        return ''


#    if request.META['SERVER_PORT'] and request.META['SERVER_PORT'] != '80':
#        return 'http://' + request.get_host() + ':' + request.META['SERVER_PORT']
#    else:
#        return 'http://' + request.get_host()


class AdminApp(AdminAppBase):
    name = 'menu'
    label = _('Menu')
    order_number = 3

    menu_items = (

        AdminLink('menu:admin:index', _('Menu entries')),
    )

    dashboard_links = [
        AdminLink(
            'menu:admin:index', _('Create menu'), models.Menu.objects.count(),
            icon_class='icon-list', perms='menu.add_menu'),
    ]

    @render_to('menu.html', use_admin=True)
    def menu(self, request, *args, **kwargs):
        return dict(app=self, menus=models.Menu.objects.all(), *args, **kwargs)

    @render_to('dashboard.html', use_admin=True)
    def dashboard(self, request, *args, **kwargs):
        return dict(app=self, *args, **kwargs)


@is_staff(required_perms='menu.change_menu')
@render_to('list_tree.html', use_admin=True)
def menu_list_tree(request, menu_slug):
    menu = get_object_or_404(models.Menu, slug=menu_slug)
    menus = models.Menu.objects.all()

    if request.method == 'POST':
        form = forms.MenuForm(request.POST, instance=menu)
        if form.is_valid():
            instance = form.save()

            return http.HttpResponseRedirect(
                path_with_port(request) + '/admin/menu/'
                + str(instance.slug) + '/')
        else:
            return {'form': form,
                    'menus': menus,
                    'object': menu}

    else:
        form = forms.MenuForm(instance=menu)

        menus = models.Menu.objects.all()
    # objects_list = paginator.current_page.object_list
        return {'form': form,
                'menus': menus,
                'object': menu}


@is_staff(required_perms='menu.add_menu')
@render_to('create.html', use_admin=True)
def create(request):
    if request.method == 'POST':
        form = forms.MenuForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return http.HttpResponseRedirect(
                path_with_port(request) + '/admin/menu/' + instance.slug + '/')
    else:
        form = forms.MenuForm()
    return {'form': form}


@is_staff(required_perms='menu.delete_menu')
@render_to('delete-menu.html', use_admin=True)
def delete(request, menu_id):
    message = ''
    status = 'ok'

    menu = get_object_or_404(models.Menu, pk=menu_id)

    if request.method == 'POST' and 'confirm' in request.POST:
        menu.delete()
        return http.HttpResponseRedirect(
            reverse('menu:admin:index'))

    return dict(message=unicode(message), status=status, instance=menu)


def generate_menu_json(menu):

    data_json = []

    def generateMenuId(item):
        if not item:
            return
        return "m" + str(item.menu_id)

    def generateItemId(item):
        if not item:
            return
        return generateMenuId(item) + "e" + str(item.id)

    def generateParentId(item):
        if not item.parent:
            return generateMenuId(item)
        else:
            return generateItemId(item.parent)

    def getIcon(item):
        if item.consumer:
            if item.consumer_type.name == 'Document':
                return "icon icon-edit"
            elif item.consumer_type.name == 'Landing':
                return "icon icon-file"
            elif item.consumer_type.name == 'Simple page':
                return "icon icon-sitemap"

        elif item.url:
            return "icon icon-link"

        else:
            return None

    def getLabel(item):
        h = {'Document': 'presscenter/edit',
             'Landing': 'landing', 'Simple page': 'simplepages'}
        return h[item.consumer_type.name]

    def getConsumer(item):
        if item.consumer:
            return dict(url=item.consumer.get_absolute_url(),
                        title=item.consumer.title,
                        admin_url='/admin/{0}/{1}/'.format(
                            getLabel(item), item.consumer_id),
                        type=item.consumer_type.name)

    children = models.MenuEntry.objects.filter(menu__id=menu.id)
    data_json.append(dict(id="m" + str(menu.id),
                          text=menu.title,
                          parent="#",
                          state={"opened": "true", "disabled": "true"},
                          icon="icon-star icon"),)
    for item in children:
        data_json.append(dict(id=generateItemId(item),
                              text=item.title,
                              parent=generateParentId(item),
                              state={"opened": "true"},
                              icon=getIcon(item),
                              consumer=getConsumer(item)))

    return data_json


@is_staff(required_perms='menu.change_menu')
@ajax_request
def menu_list_ajax(request, menu_slug):
    menu = models.Menu.objects.get(slug=menu_slug)
    return generate_menu_json(menu)


@is_staff(required_perms='menu.change_menu')
@ajax_request
def preview(request, menu_slug):
    menu = models.Menu.objects.get(slug=menu_slug)
    return TemplateResponse(
        request, 'spicy.menu/admin/preview.html', {'slug': menu.slug})


@is_staff(required_perms='menu.change_menu')
@ajax_request
def entry_move(request, entry_id):

    if request.method == 'POST':

        entry = get_object_or_404(models.MenuEntry, pk=entry_id)

        old_position = entry.position

        form = forms.PartialEntryForm(request.POST, entry)
        if form.is_valid():

            entry.position = int(request.POST.get('position'))

            if int(request.POST.get('position')) < old_position:

                entry.position -= 1  # magic, don't touch

            if request.POST.get('parent'):
                entry.parent = get_object_or_404(
                    models.MenuEntry, pk=int(request.POST.get('parent')))
            else:
                entry.parent = None
            entry.menu = models.Menu.objects.get(id=int(
                request.POST.get('menu')))

            entry.save(force_update=True)

            entries = models.MenuEntry.objects.filter(
                menu=entry.menu, parent=entry.parent)

            positions = [ent.position for ent in entries]

            p_range = [x for x in range(1, len(entries) + 1)]

            if positions != p_range:

                for i, ent in enumerate(entries):

                    if ent.position != p_range[i]:

                        ent.position = p_range[i]
                        ent.save()

            return http.HttpResponse()
        else:
            errors = form.errors
            return http.HttpResponse(simplejson.dumps(errors))

    return http.HttpResponseForbidden()


@is_staff(required_perms='menu.change_menu')
@ajax_request
def entry_copy(request, entry_id, menu_id):

    entry = get_object_or_404(models.MenuEntry, pk=entry_id)
    entry_children = entry.children.all()
    menu = get_object_or_404(models.Menu, pk=menu_id)
    if request.method == 'POST':
        form = forms.AjaxEntryForm(request.POST, instance=entry)
        if form.is_valid():
            original = form.save()

            copy = original
            copy.pk = None
            copy.parent = None
            copy.menu = menu
            copy.save()

            def copy_children(children, copy):

                for x in children:
                    child_copy = x
                    child_copy.pk = None
                    child_copy.parent = copy
                    child_copy.menu = menu
                    child_copy.save()
                    if len(x.children.all()):
                        copy_children(x.children.all(), child_copy)

            copy_children(entry_children, copy)

            return http.HttpResponse(
                path_with_port(request) + '/admin/menu/' + menu.slug + '/')
        else:
            data = simplejson.dumps(
                dict([(k, [unicode(e) for e in v])
                      for k, v in form.errors.items()]))

            return http.HttpResponseBadRequest(
                data, mimetype='application/json')
    else:
        form = forms.AjaxEntryForm(instance=entry)
    return {
        'form': form,
        'menus': models.Menu.objects.exclude(id=entry.menu.id),
        'instance_id': entry.id}


@is_staff(required_perms='menu.add_menuentry')
@render_to('create-ajax.html', use_admin=True)
def entry_add(request):
    if request.method == 'POST':
        form = forms.EntryForm(None, request.POST)
        if form.is_valid():
            instance = form.save()

            return http.HttpResponseRedirect(
                path_with_port(request) + '/admin/menu/entries/'
                + str(instance.pk) + '/')

    else:

        form = forms.EntryForm(
            initial={
                'menu': request.GET.get('menu'),
                'parent': request.GET.get('parent')},
            menuid=request.GET.get('menu'),)
    return {'form': form}


@is_staff(required_perms='menu.change_menuentry')
@render_to('edit-ajax.html', use_admin=True)
def entry_edit_ajax(request, entry_id):
    entry = get_object_or_404(models.MenuEntry, pk=entry_id)
    tree_id = "m" + str(entry.menu_id) + "e" + str(entry.id)
    if request.method == 'POST':
        form = forms.AjaxEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect(
                path_with_port(request) + '/admin/menu/entries/' +
                str(entry.id) + '/')
    else:
        form = forms.AjaxEntryForm(instance=entry)
    return {
        'form': form, 'add_url_name': _('Add sub entry'),
        'add_url': u'{url}?menu={menu}&parent={parent}'.format(
            url=reverse('menu:admin:entry-add'), menu=entry.menu_id,
            parent=entry_id),
        'menus': models.Menu.objects.exclude(id=entry.menu.id),
        'instance': entry,
        'tree_id': tree_id}


@is_staff(required_perms='menu.delete_menuentry')
@render_to('delete-menu.html', use_admin=True)
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
