import re
from html import escape, unescape

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()
URL_ATTRIBUTE_RE = re.compile(
    r"""(?P<attribute>\b(?:href|src))\s*=\s*(?P<quote>["'])(?P<url>.*?)(?P=quote)""",
    re.IGNORECASE | re.DOTALL,
)
LATEX_RE = re.compile(r"\\\[.*?\\\]|\\\(.*?\\\)", re.DOTALL)


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


def _protect_latex(value):
    placeholders = {}

    def replace(match):
        index = len(placeholders)
        marker = f"\ue000katex-formula-{index}\ue001"
        while marker in value or marker in placeholders:
            index += 1
            marker = f"\ue000katex-formula-{index}\ue001"
        placeholders[marker] = match.group()
        return marker

    return LATEX_RE.sub(replace, value), placeholders


@register.filter
def render_markdown(value):
    escaped = escape(value or "")
    escaped, placeholders = _protect_latex(escaped)
    rendered = markdown.markdown(
        escaped,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    rendered = _sanitize_url_attributes(rendered)
    for placeholder, formula in placeholders.items():
        rendered = rendered.replace(placeholder, formula)
    return mark_safe(rendered)
