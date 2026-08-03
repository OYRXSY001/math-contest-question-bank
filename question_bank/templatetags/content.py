import re
from html import escape, unescape

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()
URL_ATTRIBUTE_RE = re.compile(
    r"""(?P<attribute>\b(?:href|src))\s*=\s*(?P<quote>["'])(?P<url>.*?)(?P=quote)""",
    re.IGNORECASE,
)


def _unescape_url(value):
    for _ in range(5):
        decoded = unescape(value)
        if decoded == value:
            return decoded
        value = decoded
    return value


def _url_is_safe(value, attribute):
    decoded = _unescape_url(value).strip()
    if ":" not in decoded:
        return True

    scheme = decoded.split(":", 1)[0]
    scheme = re.sub(r"[\x00-\x20\x7f]+", "", scheme).lower()
    allowed_schemes = {"http", "https"}
    if attribute.lower() == "href":
        allowed_schemes.add("mailto")
    return scheme in allowed_schemes


def _sanitize_url_attributes(rendered):
    def replace(match):
        if _url_is_safe(match.group("url"), match.group("attribute")):
            return match.group(0)
        return ""

    return URL_ATTRIBUTE_RE.sub(replace, rendered)


def _latex_placeholders(value):
    index = 0
    while True:
        marker = f"\ue000katex-delimiter-{index}\ue001"
        placeholders = {
            r"\[": f"{marker}-display-open",
            r"\]": f"{marker}-display-close",
            r"\(": f"{marker}-inline-open",
            r"\)": f"{marker}-inline-close",
        }
        if not any(placeholder in value for placeholder in placeholders.values()):
            return placeholders
        index += 1


@register.filter
def render_markdown(value):
    escaped = escape(value or "")
    placeholders = _latex_placeholders(escaped)
    for delimiter, placeholder in placeholders.items():
        escaped = escaped.replace(delimiter, placeholder)
    rendered = markdown.markdown(
        escaped,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    rendered = _sanitize_url_attributes(rendered)
    for delimiter, placeholder in placeholders.items():
        rendered = rendered.replace(placeholder, delimiter)
    return mark_safe(rendered)
