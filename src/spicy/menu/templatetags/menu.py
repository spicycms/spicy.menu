from copy import copy
from django import template
from django.utils.safestring import mark_safe
from spicy.menu import models
from django.contrib.contenttypes.models import ContentType

register = template.Library()


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
            self.render_entry(context, tree, level=0)])

    def render_entry(self, context, tree, level, **extra_data):
        """
        Render a single entry.

        Adds some extra variables in entry context. This method calls itself
        recursively.
        """
        result = u''
        if tree:
            for entry, child_data, children in self.get_child_data(tree):
                entry_context = copy(context)
                data = {}
                children_results = []
                child_data.update(extra_data)
                if children:
                    children_results.append(
                        self.render_entry(
                            context, children, level + 1))
                child_data['children'] = mark_safe(u''.join(children_results))
                child_data['level'] = level
                child_data['is_root'] = level == 0
                entry_context['menu'] = child_data
                result += self.nodelist.render(entry_context)
        return result

    def get_child_data(self, tree):
        """
        Set entry, first, last variables for entry context.
        """
        tree_len = len(tree)
        for i, (entry, children) in enumerate(tree.iteritems()):
            data = {}
            data['entry'] = entry
            data['title'] = entry.title or unicode(
                entry.consumer if entry.has_consumer() else '')
            data['url'] = entry.url or (
                entry.has_consumer() and entry.consumer.get_absolute_url()
            ) or u''
            data['first'] = i == 0
            data['last'] = i == tree_len - 1
            yield entry, data, children


@register.tag
def menu(parser, token):
    """
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

    Example output:
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


def verbatim(parser, token):
    # Whatever is between {% verbatim %} and {% endverbatim %} will be preserved as
    # raw, unrendered template code.
    text = []
    parse_until = 'endverbatim'
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{ ', ' }}'),
        template.TOKEN_BLOCK: ('{% ', ' %}'),
        template.TOKEN_COMMENT: ('{# ', ' #}'),
    }
    # By the time this template tag is called, the template system has already
    # lexed the template into tokens. Here, we loop over the tokens until
    # {% endverbatim %} and parse them to TextNodes. We have to add the start and
    # end bits (e.g. "{{" for variables) because those have already been
    # stripped off in a previous part of the template-parsing process.
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == template.TOKEN_BLOCK and token.contents == parse_until:
            return template.TextNode(u''.join(text))
        start, end = tag_mapping[token.token_type]
        text.append(u'%s%s%s' % (start, token.contents, end))
    parser.unclosed_block_tag(parse_until)
verbatim = register.tag(verbatim)


@register.filter
def content_type_icon(obj):
    if not obj:
        return False
    ct = ContentType.objects.get_for_model(obj).name

    if ct == 'Document':
        return "icon icon-edit"
    elif ct == 'Landing':
        return "icon icon-file"
    elif ct == 'Simple page':
        return "icon icon-sitemap"
    else:
        return ""


@register.filter
def content_type_id(obj):
    if not obj:
        return False
    return ContentType.objects.get_for_model(obj).id
