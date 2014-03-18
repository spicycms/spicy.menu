from django.contrib.contenttypes.models import ContentType
from . import defaults


def get_autocomplete_choices():
    choices = []
    for param in defaults.MENU_AUTOCOMPLETE:
        try:
            model_name, manager = param[0].split(':')
        except ValueError:
            model_name = param[0]
            manager = 'objects'
        choices.append(getattr(ContentType.objects.get_by_natural_key(
            *model_name.split('.')).model_class(), manager).all())
    return choices


def get_autocomplete_search_fields():
    return [param[1] for param in defaults.MENU_AUTOCOMPLETE]
