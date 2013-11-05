from django.conf import settings

LABELS_CONSUMER = getattr(settings, 'LABELS_CONSUMER', None)

MENU_ENTRY_PER_PAGE = getattr(settings, 'MENU_ENTRY_PER_PAGE', 30)
