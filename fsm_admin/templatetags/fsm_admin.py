from __future__ import unicode_literals

from django import template
from django.contrib.admin.templatetags.admin_modify import submit_row
from django.conf import settings

register = template.Library()

import logging
logger = logging.getLogger(__name__)

FSM_SUBMIT_BUTTON_TEMPLATE = 'fsm_admin/fsm_submit_button.html'
FSM_SUBMIT_LINE_TEMPLATE = 'fsm_admin/fsm_submit_line.html'
if 'grappelli' in settings.INSTALLED_APPS:
    FSM_SUBMIT_BUTTON_TEMPLATE = 'fsm_admin/fsm_submit_button_grappelli.html'
    FSM_SUBMIT_LINE_TEMPLATE = 'fsm_admin/fsm_submit_line_grappelli.html'
if 'suit' in settings.INSTALLED_APPS:
    FSM_SUBMIT_BUTTON_TEMPLATE = 'fsm_admin/fsm_submit_button_suit.html'
    FSM_SUBMIT_LINE_TEMPLATE = 'fsm_admin/fsm_submit_line_suit.html'


@register.inclusion_tag(FSM_SUBMIT_BUTTON_TEMPLATE)
def fsm_submit_button(transition):
    """
    Render a submit button that requests an fsm state transition for a
    single state.
    """
    fsm_field_name, button_value, transition_name = transition
    return {
        'button_value': button_value,
        'fsm_field_name': fsm_field_name,
        'transition_name': transition_name,
    }


@register.inclusion_tag(FSM_SUBMIT_LINE_TEMPLATE, takes_context=True)
def fsm_submit_row(context):
    """
    Additional context added to an overridded submit row that adds links
    to change the state of an FSMField.
    """
    original = context.get('original', None)
    model_name = original.__class__._meta.verbose_name if original else ''

    def button_name(transition):
        if hasattr(transition, 'custom') and 'button_name' in transition.custom:
            return transition.custom['button_name']
        else:
            # Make the function name the button title, but prettier
            return '{0} {1}'.format(transition.name.replace('_',' '), model_name).title()

    # The model admin defines which field we're dealing with
    # and has some utils for getting the transitions.
    request = context['request']
    model_admin = context.get('adminform').model_admin
    transitions = model_admin._fsm_get_transitions(original, request)

    ctx = submit_row(context)
    ctx['transitions'] = []
    for field,field_transitions in iter(transitions.items()):
        ctx['transitions'] += [(field, button_name(t), t.name) for t in field_transitions]
    ctx['perms'] = context['perms']

    return ctx


@register.inclusion_tag('fsm_admin/fsm_transition_hints.html', takes_context=True)
def fsm_transition_hints(context):
    """
    Displays hints about why a state transition might not be applicable for
    this the model.
    """
    original = context.get('original', None)
    if not original:
        return {}

    model_admin = context.get('adminform').model_admin
    return {
        'transition_hints': model_admin.get_transition_hints(original)
    }
