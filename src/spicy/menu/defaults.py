from django.conf import settings

LABELS_CONSUMER = getattr(settings, 'LABELS_CONSUMER', None)

MENU_AUTOCOMPLETE = getattr(settings, 'MENU_AUTOCOMPLETE', ())
# Format for autocomplete settings:
# ('app.model[:manager]', ('field1', 'field2',...))
