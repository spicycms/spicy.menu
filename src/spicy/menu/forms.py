import autocomplete_light
from autocomplete_light.generic import GenericModelForm
from django import forms
from . import models, utils


class MenuForm(forms.ModelForm):
    class Meta:
        model = models.Menu


class AutocompleteMenuEntries(autocomplete_light.AutocompleteGenericBase):
    choices = utils.get_autocomplete_choices()
    search_fields = utils.get_autocomplete_search_fields()

autocomplete_light.register(AutocompleteMenuEntries)


class EntryForm(GenericModelForm):
    consumer = autocomplete_light.GenericModelChoiceField(
        required=False,
        widget=autocomplete_light.ChoiceWidget(
            autocomplete=AutocompleteMenuEntries,
            attrs={'minimum_characters': 0}))

    class Meta:
        model = models.MenuEntry
        fields = 'menu', 'parent', 'title', 'url', 'position'
