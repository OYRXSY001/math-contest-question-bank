import json
import re
import subprocess

from django.conf import settings

FORMULA_RE = re.compile(r"\\\[(.*?)\\\]|\\\((.*?)\\\)", re.DOTALL)


def extract_formulas(markdown_text):
    return [
        block or inline
        for block, inline in FORMULA_RE.findall(markdown_text or "")
    ]


def validate_markdown_formulas(items):
    issues = []
    formulas = []
    sources = []

    for source, text in items:
        text = text or ""
        if text.count(r"\(") != text.count(r"\)"):
            issues.append(f"{source}: 行内公式定界符不成对")
        if text.count(r"\[") != text.count(r"\]"):
            issues.append(f"{source}: 块级公式定界符不成对")
        for formula in extract_formulas(text):
            formulas.append(formula)
            sources.append(source)

    if not formulas:
        return issues

    try:
        result = subprocess.run(
            ["node", str(settings.BASE_DIR / "scripts" / "validate-katex.mjs")],
            input=json.dumps(formulas, ensure_ascii=False),
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
            cwd=settings.BASE_DIR,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return [*issues, f"KaTeX 校验器无法运行: {error}"]

    if result.returncode != 0:
        return [*issues, f"KaTeX 校验器退出码 {result.returncode}: {result.stderr.strip()}"]

    for error in json.loads(result.stdout or "[]"):
        issues.append(f"{sources[error['index']]}: {error['message']}")
    return issues
