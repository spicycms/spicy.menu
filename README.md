spicy.menu
==========
Приложение Django для SpicyCMS, использует [концепцию реиспользования кода и конфигурации spicy.core](https://github.com/spicycms/spicy.core), реализует модели для управления меню и его структурой на страницах сайта.

Модуль совместим с Django 1.3 - 1.5.12.

## Назначение

Это простое приложение позволяет  создавать блоки меню для вашего сайта, структуру меню с подпунктами, совместно с использованием [spicy.core.simplepages](https://github.com/spicycms/spicy.core/tree/develop/docs/simplepages#spicycoresimplepages) задавать верстку через админку, не редактируя html-шаблоны в файловой системе.


## Для редактора сайта
Преимущество spicy.menu в том, что меню формируется динамически. Вы можете разместить html-код меню на вашей странице, и после этого многократно редактировать структуру меню только через админку, без модификации html-шаблонов. Для этого в верху вашей html-странцы укажите:
```
{% load menu %}
```

И разместите этот код, в блоке, заготовленном для меню:
```
{% menu slug %}
    {% if menu.first %}
    <ul class='l{{ menu.level }}'>
    {% endif %}    
      <li>
        {% if menu.is_root %}<h2>{{ menu.title }}</h2>
        {% else %}{{ menu.title }}
        {% endif %}
        {{ menu.children }}
      </li>
    {% if menu.last %}
    </ul>
    {% endif %}
{% endmenu %}
```
Пример, результата, который будет добавлен в html-шаблон этим кодом:
```
<ul>
    <li>
      <h2>Top level menu</h2>
    </li>
    <li>
      <h2>Second top menu entry</h2>
      <ul>
        <li>
          Submenu
        </li>
        <li>
          Another submenu
        </li>
      </ul>
    </li>
</ul>
```

Более того, вы можете не работать с html-кодом в файловой системе, а изменять ваши страницы напрямую через админку, в том числе, размещать на них код меню. Об этой возможности SpicyCMS более подробно в [документации spicy.core.simplepages](https://github.com/spicycms/spicy.core/tree/develop/docs/simplepages#spicycoresimplepages).

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
* ``MENU_AUTOCOMPLETE`` - список, определяющий выпадающие значения для автокомплитера. Использутеся в админке, при добавление подпункта меню. По умолчанию - пустой список ``[]``

## Refactoring
Не используются настройки:
* defaults.LABELS_CONSUMER
