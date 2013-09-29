import itertools
from collections import OrderedDict
from django.db import models
from django.utils.translation import ugettext_lazy as _
from spicy.core.service.models import ProviderModel
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
        for entry, children in grouped_entries.items():
            if entry is parent:
                del grouped_entries[entry]
                for child in children:
                    child_node = OrderedDict()
                    tree_node[child] = child_node
                    for child in children:
                        tree_node[child] = self._collect_children(
                            grouped_entries, child.id, child_node) or None
        return tree_node


class MenuEntry(ProviderModel):
    menu = models.ForeignKey(Menu, verbose_name=_('Menu'))
    parent = models.ForeignKey(
        'self', null=True, blank=True, verbose_name=_('Parent'),
        related_name='children')
    title = models.CharField(_('Title'), max_length=255)
    position = models.PositiveSmallIntegerField(_('Position'))

    class Meta:
        db_table = 'mn_entry'
        ordering = 'menu', 'position',

    def __unicode__(self):
        return self.title

