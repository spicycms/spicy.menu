# -*- coding: utf-8 -*-
import autocomplete_light
from autocomplete_light.generic import GenericModelForm
from autocomplete_light.autocomplete.template import AutocompleteTemplate
from django import forms
from . import models, utils
from django.utils.translation import ugettext_lazy as _
from django.forms.models import ModelChoiceField
from django.forms.widgets import HiddenInput


class MenuForm(forms.ModelForm):

    class Meta:
        model = models.Menu


try:
    class AutocompleteMenuEntries(autocomplete_light.AutocompleteGenericBase,
                                  AutocompleteTemplate):
        choices = utils.get_autocomplete_choices()
        search_fields = utils.get_autocomplete_search_fields()

    autocomplete_light.register(
        AutocompleteMenuEntries,
        choice_template='spicy.menu/admin/autocomplete.html')

    class EntryForm(GenericModelForm):
        menu = ModelChoiceField(
            queryset=models.Menu.objects.all(), widget=HiddenInput())

        consumer = autocomplete_light.GenericModelChoiceField(
            required=False,
            label=_('Object'),
            help_text=_('Choose an object for this menu entry'),
            widget=autocomplete_light.ChoiceWidget(
                autocomplete=AutocompleteMenuEntries,
                attrs={'minimum_characters': 0}))

        class Meta:
            model = models.MenuEntry
            fields = 'menu', 'parent', 'title', 'url'

        def __init__(self, menuid, *args, **kwargs):
            super(EntryForm, self).__init__(*args, **kwargs)
            try:
                if menuid:
                    self.fields['parent'].queryset = \
                        models.MenuEntry.objects.filter(
                            menu_id=menuid)

            except:
                raise

        def clean(self):

            cleaned_data = super(EntryForm, self).clean()

            url = cleaned_data.get("url")
            consumer = cleaned_data.get("consumer")

            if not url and not consumer:

                msg = _('Please fill Object or Url field')
                self._errors["url"] = self.error_class([msg])
                self._errors["consumer"] = self.error_class([msg])

                del cleaned_data["url"]
                del cleaned_data["consumer"]

            # Always return the full collection of cleaned data.
            return cleaned_data
except:
    pass


class PartialEntryForm(forms.ModelForm):

    class Meta:
        model = models.MenuEntry
        fields = 'menu', 'parent', 'position'


try:

    class AjaxEntryForm(GenericModelForm):
        consumer = autocomplete_light.GenericModelChoiceField(
            required=False,
            label=_('Object'),
            help_text=_('Choose an object for this menu entry '),
            widget=autocomplete_light.ChoiceWidget(
                autocomplete=AutocompleteMenuEntries,
                attrs={'minimum_characters': 0}))

        class Meta:
            model = models.MenuEntry
            fields = 'title', 'url'

        def clean(self):

            cleaned_data = super(AjaxEntryForm, self).clean()

            url = cleaned_data.get("url")
            consumer = cleaned_data.get("consumer")

            if not url and not consumer:

                msg = _('Please fill Object or Url field')

                self._errors["consumer"] = self.error_class([msg])
                self._errors["url"] = self.error_class([msg])

                del cleaned_data["url"]
                del cleaned_data["consumer"]

            # Always return the full collection of cleaned data.
            return cleaned_data
except:
    pass
