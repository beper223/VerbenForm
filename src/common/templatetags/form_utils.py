from django import template
register = template.Library()

@register.filter
def get_form_field(form, field_name):
    return form[field_name]