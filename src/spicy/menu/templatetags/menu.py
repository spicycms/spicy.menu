from django import templeate

register = templeate.Library()


class MenuNode(template.Node):
    def __init__(self, slug, nodelist):
        self.slug = template.Variable(slug)
        self.nodelist = nodelist

    def render(self, context):
        slug = self.slug.resolve(context)

        try:
            menu = models.Menu.objects.get(slug=slug)
        except models.Menu.DoesNotExist:
            return '<!-- menu with slug ' + slug + ' doesn\'t exist'
        
        return self.render_entries(context, menu.get_tree())

    def render_entries(self, context, tree):
        """
        Render node list starting from tree top.
        """
        return u''.join([
            self.render_entry(
                context, entry, children, {'is_root': True}, **data)
            for entry, children in tree.iteritems()])
        
    def render_entry(self, context, entry, children, extra_data=None, **data):
        """
        Render a single entry.

        Adds some extra variables in entry context. This method calls itself
        recursively.
        """
        entry_context = context.copy()
        menu = {}
        entry_context['menu'] = menu
        menu.update(data)
        if children:
            menu['children'] = u''.join([
                self.render_entry(context, entry, child, **child_data)
                for child, child_data in self.get_child_data(
                    children, extra_data)])
        return self.nodelist.render(entry_context)

    def get_child_data(self, children, extra_data):
        """
        Set entry, first, last variables for entry context.
        """
        num_children = len(children)
        for i, child in enumerate(children):
            data = {}
            data['entry'] = child
            data['first'] = i == 0
            data['last'] = i == num_children - 1
            if extra_data:
                data.update(extra_data)
            yield child, data


@register.tag
def menu(parser, token):
    """
    {% menu slug %}
    {% if menu.first %}
    <ul>
    {% endif %}    
      <li>
        {% if menu.is_root %}<h2>{{ menu.entry.title }}</h2>
        {% else %}{{ menu.entry.title }}
        {% endif %}
        {{ menu.children }}
      </li>
    {% if menu.last %}
    </ul>
    {% endif %}
    {% endmenu %}

    Example outpute:
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
    """
   try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires slug argument" % token.contents.split()[0])

    nodelist = parser.parse(('endmenu',))
    parser.delete_first_token()
    return MenuNode(arg, nodelist)
