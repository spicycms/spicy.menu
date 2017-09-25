spicy.menu
==========
Приложение Django для SpicyCMS, использует [концепцию реиспользования кода и конфигурации spicy.core] (https://github.com/spicycms/spicy.core), реализует модели для управления меню и его структурой на страницах сайта.

Модуль совместим с Django 1.3 - 1.5.12.

## Назначение

Это простое приложение позволяет  создавать блоки меню для вашего сайта, структуру меню с подпунктами, совместно с использованием [spicy.core.simplepages](https://github.com/spicycms/spicy.core/tree/develop/docs/simplepages#spicycoresimplepages) задавать верстку через админку, не редактируя html-шаблоны в файловой системе.


## Для редактора сайта


## Для Django-программиста

Установите модуль с помощью pip: ``pip install git+https://github.com/spicycms/spicy.menu.git``.

При использовании сборки SpicyCMS, для подключения модуля spicy.menu, достаточно добавить его в settings.py:
```
INSTALLED_APPS = [
  ...
  'spicy.menu',
  ...
]
```
Теперь необходимо выполнить ``manage.py syncdb``, чтобы Django создала таблицу для объектов spicy.menu в базе данных.

## Настройки spicy.menu
* 

## Refactoring
Не используются настройки:
* defaults.LABELS_CONSUMER
