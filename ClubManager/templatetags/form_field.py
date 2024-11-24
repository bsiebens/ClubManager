from django import template
from django.forms import BoundField

register = template.Library()

@register.inclusion_tag("templatetags/field.html")
def form_field(field: BoundField, label: str | None = None, help_text: str | None = None, show_label: bool = True, show_help_text: bool = True,
               show_placeholder: bool = True, show_as_toggle: bool = False, size: str = "full") -> dict:
    if label is not None:
        field.label = label

    if help_text is not None:
        field.help_text = help_text

    field_type = None
    match field.widget_type:
        case "select" | "nullbooleanselect" | "radioselect":
            field_type = "select"
        case "checkbox":
            field_type = "checkbox"
        case "textarea" | "markdownx":
            field_type = "textarea"
        case "clearablefile":
            field_type = "file"
        case "selectmultiple":
            field_type = "select"
        case _:
            field_type = "input"

    size_modifier = None
    match size:
        case "extra-small":
            size_modifier = "xs"
        case "small":
            size_modifier = "sm"
        case _:
            pass

    return {"field": field, "show_label": show_label, "show_help_text": show_help_text, "show_placeholder": show_placeholder, "show_as_toggle": show_as_toggle, "field_type": field_type, "size_modifier": size_modifier}