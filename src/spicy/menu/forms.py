from django import forms
from django.utils.translation import ugettext_lazy as _
from . import models


class MenuForm(forms.ModelForm):
    class Meta:
        model = models.Menu


class EntryForm(forms.ModelForm):
    class Meta:
        model = models.MenuEntry
