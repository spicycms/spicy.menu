import itertools
from collections import OrderedDict
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _
from . import defaults


class Menu(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    slug = models.SlugField(_('Slug'))

    class Meta:
        db_table = 'mn_menu'
        ordering = 'title',

    def __unicode__(self):
        return self.title

    def get_tree(self):
        """
        Fetch all entries as a tree, without issuing unnecessary queries.
        """
        # Create a dict with mapping of {id: entry}
        entries_dict = dict(
            (entry.pk, entry) for entry in self.menuentry_set.all())

        # Set all parents.
        for entry in entries_dict.values():
            entry.parent = entries_dict.get(entry.parent_id)

        # Group into {parent_id: entry} dict.
        entries_list = sorted(
            entries_dict.values(), key=lambda item: item.parent_id)
        grouped_entries = dict(
            (key, list(value)) for key, value in itertools.groupby(
                entries_list, lambda entry: entry.parent_id))

        # Build the tree!
        return self._collect_children(grouped_entries, None, OrderedDict())

    def _collect_children(self, grouped_entries, parent, tree_node):
        """
        Collect children from grouped entries recursively.
        """
        # For every bug in code below God will kill a kitten. There better be
        # none!
        for entry, children in grouped_entries.items():
            if entry is parent:
                del grouped_entries[entry]
                for child in children:
                    child_node = OrderedDict()
                    tree_node[child] = child_node
                    self._collect_children(
                        grouped_entries, child.id, child_node)
        return tree_node


class MenuEntry(models.Model):
    menu = models.ForeignKey(Menu, verbose_name=_('Menu'))
    parent = models.ForeignKey(
        'self', null=True, blank=True, verbose_name=_('Parent'),
        related_name='children')
    consumer_type = models.ForeignKey(ContentType, null=True, blank=True)
    consumer_id = models.PositiveIntegerField(null=True, blank=True)
    consumer = generic.GenericForeignKey(
        ct_field='consumer_type', fk_field='consumer_id')
    title = models.CharField(_('Title'), max_length=255, blank=True)
    url = models.CharField(
        _('URL'), max_length=255, blank=True,
        help_text=_('Use if no content is attached'))
    position = models.PositiveSmallIntegerField(_('Position'))

    class Meta:
        db_table = 'mn_entry'
        ordering = 'menu', 'parent__position', 'position',

    def __unicode__(self):
        return self.title

