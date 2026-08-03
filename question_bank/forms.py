from django import forms

from .models import Paper, Question
from .taxonomy import TAXONOMY


KNOWLEDGE_CHOICES = [
    (child_slug, child_name)
    for _, _, _, children in TAXONOMY
    for child_name, child_slug in children
]


class QuestionFilterForm(forms.Form):
    edition = forms.TypedChoiceField(
        required=False,
        coerce=int,
        empty_value=None,
        choices=[("", "全部届数")] + [(number, f"第{number}届") for number in range(1, 18)],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    stage = forms.ChoiceField(
        required=False,
        choices=[("", "全部阶段"), *Paper.Stage.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    question_type = forms.ChoiceField(
        required=False,
        choices=[("", "全部题型"), *Question.Type.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    knowledge = forms.MultipleChoiceField(
        required=False,
        choices=KNOWLEDGE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )
    q = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.SearchInput(
            attrs={"class": "form-control", "placeholder": "输入题干或解析关键词"}
        ),
    )
