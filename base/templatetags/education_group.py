##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django import template
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils import six
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from backoffice.settings import base
from base.business.education_groups.perms import is_eligible_to_delete_education_group, \
    is_eligible_to_change_education_group, is_eligible_to_add_training, \
    is_eligible_to_add_mini_training, is_eligible_to_add_group
from base.business.group_element_years.management import EDUCATION_GROUP_YEAR, LEARNING_UNIT_YEAR
from base.models.education_group_year import EducationGroupYear
from base.models.learning_unit_year import LearningUnitYear

OPTIONAL_PNG = base.STATIC_URL + 'img/education_group_year/optional.png'
MANDATORY_PNG = base.STATIC_URL + 'img/education_group_year/mandatory.png'
CASE_JPG = base.STATIC_URL + 'img/education_group_year/case.jpg'

CHILD_BRANCH_REMARK = """\
        <div style="word-break: keep-all;margin-left: 14px;">
            {remark}
        </div>
"""

CHILD_BRANCH_COMMENT = """\
        <div style="word-break: keep-all;margin-left: 14px;">
            ({comment})
        </div>
"""

CHILD_BRANCH_START = """\
<tr>
    <td style="padding-left:{padding}em;float:left;">
        <div style="word-break: keep-all;">
            <img src="{icon_list_2}" height="10" width="10">
            {value}
"""

CHILD_BRANCH_END = """\
            {sublist}
        </div>
    </td>
</tr>
"""

CHILD_LEAF_COMMENT = """\
        <div style="word-break: keep-all;margin-left:27px;">
            ({comment})
        </div>
"""

CHILD_LEAF_START = """\
<tr>
    <td style="padding-left:{padding}em;float:left;">
        <img src="{icon_list_1}" height="14" width="17">
        <img src="{icon_list_2}" height="10" width="10">
    </td>
    <td style="float:left;">
        {value}
"""

CHILD_LEAF_END = """\
        {sublist}
    </td>
    <td style="text-align: center;">{an_1}</td>
    <td style="text-align: center;">{an_2}</td>
    <td style="text-align: center;">{an_3}</td>
</tr>
"""

NO_GIVEN_ROOT = "INVALID TREE : no given root"
ICON_JSTREE_FILE = "data-jstree='{\"icon\":\"jstree-icon jstree-file\"}'"
ICON_JSTREE_LEAF = "data-jstree='{\"icon\":\"glyphicon glyphicon-leaf\"}'"

# TODO use inclusion tag
LI_TEMPLATE = """
<li class="{}" id="{}">
    <a href="{}" data-toggle="tooltip" title="{}">{}</a>
</li>
"""

BUTTON_TEMPLATE = """
<button title="{}" class="btn btn-default btn-sm" id="{}" data-toggle="tooltip-wrapper" name="action" {}>
    <i class="fa {}"></i>
</button>
"""

BUTTON_ORDER_TEMPLATE = """
<button type="submit" title="{}" class="btn btn-default btn-sm" 
    id="{}" data-toggle="tooltip-wrapper" name="action" value="{}" {}>
    <i class="fa {}"></i>
</button>
"""

ICONS = {
    "up": "fa-arrow-up",
    "down": "fa-arrow-down",
    "detach": "fa-close",
    "edit": "fa-edit",
}

BRANCH_TEMPLATE = """
<ul>
    <li {data_jstree} id="node_{gey}_{obj_pk}_{obj_type}">
        <a href="{url}" class="{a_class}" title="{tooltip_msg}">
            {text}
        </a>
        {children}
    </li>
</ul>
"""

register = template.Library()


@register.simple_tag(takes_context=True)
def li_with_deletion_perm(context, url, message, url_id="link_delete"):
    return li_with_permission(context, is_eligible_to_delete_education_group, url, message, url_id)


@register.simple_tag(takes_context=True)
def li_with_update_perm(context, url, message, url_id="link_update"):
    return li_with_permission(context, is_eligible_to_change_education_group, url, message, url_id)


@register.simple_tag(takes_context=True)
def li_with_create_perm_training(context, url, message, url_id="link_create_training"):
    return li_with_permission(context, is_eligible_to_add_training, url, message, url_id)


@register.simple_tag(takes_context=True)
def li_with_create_perm_mini_training(context, url, message, url_id="link_create_mini_training"):
    return li_with_permission(context, is_eligible_to_add_mini_training, url, message, url_id)


@register.simple_tag(takes_context=True)
def li_with_create_perm_group(context, url, message, url_id="link_create_group"):
    return li_with_permission(context, is_eligible_to_add_group, url, message, url_id)


def li_with_permission(context, permission, url, message, url_id):
    permission_denied_message, disabled, root = _get_permission(context, permission)

    if not disabled:
        href = url
    else:
        href = "#"

    return mark_safe(LI_TEMPLATE.format(disabled, url_id, href, permission_denied_message, message))


def _get_permission(context, permission):
    permission_denied_message = ""

    education_group_year = context.get('education_group_year')
    person = context.get('person')
    root = context["request"].GET.get("root", "")

    try:
        result = permission(person, education_group_year, raise_exception=True)

    except PermissionDenied as e:
        result = False
        permission_denied_message = str(e)

    return permission_denied_message, "" if result else "disabled", root


@register.simple_tag(takes_context=True)
def button_order_with_permission(context, title, id_button, value):
    permission_denied_message, disabled, root = _get_permission(context, is_eligible_to_change_education_group)

    if disabled:
        title = permission_denied_message

    if value == "up" and context["forloop"]["first"]:
        disabled = "disabled"

    if value == "down" and context["forloop"]["last"]:
        disabled = "disabled"

    return mark_safe(BUTTON_ORDER_TEMPLATE.format(title, id_button, value, disabled, ICONS[value]))


@register.simple_tag(takes_context=True)
def button_with_permission(context, title, id_a, value):
    permission_denied_message, disabled, root = _get_permission(context, is_eligible_to_change_education_group)

    if disabled:
        title = permission_denied_message

    return mark_safe(BUTTON_TEMPLATE.format(title, id_a, disabled, ICONS[value]))


@register.filter(is_safe=True, needs_autoescape=True)
def pdf_tree_list(value, autoescape=True):
    if autoescape:
        escaper = conditional_escape
    else:
        def escaper(x):
            return x
    return mark_safe(list_formatter(value))


def walk_items(item_list):
    if item_list:
        item_iterator = iter(item_list)
        try:
            item = next(item_iterator)
            while True:
                try:
                    next_item = next(item_iterator)
                except StopIteration:
                    yield item, None
                    break
                if not isinstance(next_item, six.string_types):
                    try:
                        iter(next_item)
                    except TypeError:
                        pass
                    else:
                        yield item, next_item
                        item = next(item_iterator)
                        continue
                yield item, None
                item = next_item
        except StopIteration:
            pass
    else:
        return ""


def list_formatter(item_list, tabs=1, depth=None):
    output = []
    depth = depth if depth else 1
    for item, children in walk_items(item_list):
        sublist = ''
        padding = 2 * depth
        if children:
            sublist = '%s' % (
                list_formatter(children, tabs + 1, depth + 1))
        append_output(item, output, padding, sublist)
    return '\n'.join(output)


def append_output(item, output, padding, sublist):
    if item.child_leaf:
        output.append(
            CHILD_LEAF_START.format(
                padding=padding,
                icon_list_1=CASE_JPG,
                icon_list_2=get_mandatory_picture(item),
                value=escaper(force_text(item.verbose)))
        )

        if item.comment:
            output.append(
                CHILD_LEAF_COMMENT.format(
                    icon_list_1=CASE_JPG,
                    icon_list_2=get_mandatory_picture(item),
                    comment=item.verbose_comment))

        output.append(
            CHILD_LEAF_END.format(sublist=sublist,
                                  width_an="15px",
                                  an_1=check_block(item, "1"),
                                  an_2=check_block(item, "2"),
                                  an_3=check_block(item, "3"))
        )

    else:
        output.append(
            CHILD_BRANCH_START.format(
                padding=padding,
                icon_list_2=get_mandatory_picture(item),
                value=escaper(force_text(item.verbose)))
        )

        if item.child.verbose_remark:
            output.append(
                CHILD_BRANCH_REMARK.format(
                    icon_list_2=get_mandatory_picture(item),
                    remark=item.child.verbose_remark)
            )

        if item.comment:
            output.append(
                CHILD_BRANCH_COMMENT.format(
                    icon_list_2=get_mandatory_picture(item),
                    comment=item.verbose_comment)
            )

        output.append(
            CHILD_BRANCH_END.format(sublist=sublist)
        )


def get_mandatory_picture(item):
    return MANDATORY_PNG if item.is_mandatory else OPTIONAL_PNG


def check_block(item, value):
    return "X" if item.block and value in item.block else ""


def escaper(x):
    return x


@register.simple_tag(takes_context=True)
def build_tree(context, current_group_element_year, selected_node_obj):
    request = context["request"]
    root = context["root"]

    # If it is the root, the group_element_year is not yet available.
    education_group_year = root if not current_group_element_year else current_group_element_year.child_branch

    if not selected_node_obj:
        selected_node_obj = education_group_year

    children_template = ""
    for child in education_group_year.group_element_year_branches:
        children_template += build_tree(context, child, selected_node_obj)

    for child in education_group_year.group_element_year_leaves_with_annotate_on_prerequisites(root.id):
        luy = child.child_leaf
        has_prerequistes = child.has_prerequisites
        children_template += _generate_branch_html(luy, selected_node_obj, child, root, request, "",
                                                   has_prerequistes=has_prerequistes)

    return _generate_branch_html(education_group_year, selected_node_obj, current_group_element_year,
                                 root, request, children_template)


def _generate_branch_html(node_obj, selected_node_obj, current_group_element_year, root, request, children_template,
                          has_prerequistes=False):
    if isinstance(node_obj, EducationGroupYear):
        format_data = _prepare_education_group_node_data(node_obj, selected_node_obj, current_group_element_year, root,
                                                         children_template, request)
    else:
        format_data = _prepare_learning_unit_node_data(node_obj, selected_node_obj, current_group_element_year, root,
                                                       request, has_prerequistes)
    return mark_safe(BRANCH_TEMPLATE.format(
        **format_data
    ))


def _prepare_learning_unit_node_data(luy_obj, selected_node_obj, current_group_element_year, root, request,
                                     has_prerequisites):
    data_jstree = _get_icon_jstree(luy_obj, has_prerequisites=has_prerequisites)
    gey = _get_group_element_year_id(current_group_element_year)
    obj_pk = luy_obj.pk
    url = _get_node_url(request, luy_obj, selected_node_obj, root, current_group_element_year)
    text = luy_obj.acronym
    a_class = _get_a_class(luy_obj, selected_node_obj)
    children = ""
    tooltip_msg = luy_obj.complete_title
    return {
        'data_jstree': data_jstree,
        'gey': gey,
        'obj_pk': obj_pk,
        'obj_type': LEARNING_UNIT_YEAR,
        'url': url,
        'a_class': a_class,
        'tooltip_msg': tooltip_msg,
        'text': text,
        'children': children
    }


def _prepare_education_group_node_data(egy_obj, selected_node_obj, current_group_element_year, root, children_template,
                                       request):
    data_jstree = _get_icon_jstree(egy_obj)
    gey = _get_group_element_year_id(current_group_element_year)
    obj_pk = egy_obj.pk
    url = _get_node_url(request, egy_obj, selected_node_obj, root, current_group_element_year)
    text = egy_obj.verbose
    a_class = _get_a_class(egy_obj, selected_node_obj)
    children = children_template
    tooltip_msg = egy_obj.acronym
    return {
        'data_jstree': data_jstree,
        'gey': gey,
        'obj_pk': obj_pk,
        'obj_type': EDUCATION_GROUP_YEAR,
        'url': url,
        'a_class': a_class,
        'tooltip_msg': tooltip_msg,
        'text': text,
        'children': children
    }


def _get_group_element_year_id(current_group_element_year):
    return current_group_element_year.pk if current_group_element_year else "0"


def _get_node_url(request, node_obj, selected_node_obj, root, current_group_element_year):
    default_url_name = _get_default_url_name(node_obj)

    url_name = request.resolver_match.url_name if request.resolver_match and type(node_obj) == type(selected_node_obj) \
        else default_url_name

    return reverse(url_name, args=[root.pk, node_obj.pk]) + "?group_to_parent=" + (
        str(current_group_element_year.id) if current_group_element_year else '0')


def _get_default_url_name(node_obj):
    DEFAULT_URL_BY_NODE_TYPE = {
        LearningUnitYear: "learning_unit_utilization",
        EducationGroupYear: "education_group_read",
    }
    return DEFAULT_URL_BY_NODE_TYPE[type(node_obj)]


def _get_icon_jstree(node_obj, has_prerequisites=False):
    if isinstance(node_obj, EducationGroupYear):
        return ""
    return ICON_JSTREE_LEAF if has_prerequisites else ICON_JSTREE_FILE


def _get_a_class(node_obj, selected_node_obj):
    return "jstree-wholerow-clicked" \
        if node_obj.pk == selected_node_obj.pk and type(node_obj) == type(selected_node_obj) \
        else ""


@register.simple_tag(takes_context=True)
def url_resolver_match(context):
    return context.request.resolver_match.url_name


@register.simple_tag(takes_context=True)
def link_detach_education_group(context):
    return _custom_link_education_group(context, action="Detach", onclick="""onclick="select()" """)


@register.simple_tag(takes_context=True)
def link_pdf_content_education_group(context):
    return _custom_link_pdf_content(context, action="Generate pdf", onclick="")


def _custom_link_education_group(context, action, onclick):
    if context['can_change_education_group'] and context['group_to_parent'] != '0':
        li_attributes = """ id="btn_operation_detach_{group_to_parent}" """.format(
            group_to_parent=context['group_to_parent']
        )
        a_attributes = """ href="#" title="{title}" {onclick} """.format(title=_(action), onclick=onclick)
    else:
        li_attributes = """ class="disabled" """
        title = ""
        if not context['can_change_education_group']:
            title += _("The user has not permission to change education groups.")
        if context['group_to_parent'] == '0':
            title += " " + _("It is not possible to {action} the root element.".format(action=str.lower(action)))

        a_attributes = """ title="{title}" """.format(title=title)
    text = _(action)
    html_template = """
        <li {li_attributes}>
            <a {a_attributes} data-toggle="tooltip">{text}</a>
        </li>
    """

    return mark_safe(
        html_template.format(
            li_attributes=li_attributes,
            a_attributes=a_attributes,
            text=text,
        )
    )


def _custom_link_pdf_content(context, action, onclick):
    li_attributes = """ id="btn_operation_pdf_content" """
    a_attributes = """ href="#" title="{title}" {onclick} """.format(title=_(action), onclick=onclick)

    text = _(action)
    html_template = """
        <li {li_attributes}>
            <a {a_attributes} data-toggle="tooltip">{text}</a>
        </li>
    """

    return mark_safe(
        html_template.format(
            li_attributes=li_attributes,
            a_attributes=a_attributes,
            text=text,
        )
    )
