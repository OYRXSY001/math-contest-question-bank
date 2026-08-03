from html import escape

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render_markdown(value):
    escaped = escape(value or "")
    delimiters = {
        r"\[": "\ue000",
        r"\]": "\ue001",
        r"\(": "\ue002",
        r"\)": "\ue003",
    }
    for delimiter, placeholder in delimiters.items():
        escaped = escaped.replace(delimiter, placeholder)
    rendered = markdown.markdown(
        escaped,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    for delimiter, placeholder in delimiters.items():
        rendered = rendered.replace(placeholder, delimiter)
    return mark_safe(rendered)
