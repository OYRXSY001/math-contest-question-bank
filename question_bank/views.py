from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .forms import QuestionFilterForm
from .models import Paper, Question
from .queries import filtered_questions, with_user_flags


def home(request):
    return render(
        request,
        "home.html",
        {"filter_form": QuestionFilterForm(), "editions": range(1, 18)},
    )


def _listing_response(request, force_questions=False):
    questions, form = filtered_questions(request.GET)
    question_mode = force_questions or bool(
        request.GET.get("q")
        or request.GET.get("question_type")
        or request.GET.getlist("knowledge")
    )
    empty_search = force_questions and not any(
        (
            request.GET.get("q", "").strip(),
            request.GET.get("edition"),
            request.GET.get("stage"),
            request.GET.get("question_type"),
            request.GET.getlist("knowledge"),
        )
    )
    if empty_search:
        questions = questions.none()

    if question_mode:
        page_obj = Paginator(with_user_flags(questions, request.user), 20).get_page(
            request.GET.get("page")
        )
    else:
        papers = Paper.objects.filter(status=Paper.Status.PUBLISHED)
        if form.is_valid():
            if form.cleaned_data["edition"]:
                papers = papers.filter(edition=form.cleaned_data["edition"])
            if form.cleaned_data["stage"]:
                papers = papers.filter(stage=form.cleaned_data["stage"])
        else:
            papers = papers.none()
        page_obj = Paginator(papers, 20).get_page(request.GET.get("page"))

    return render(
        request,
        "question_bank/paper_list.html",
        {
            "filter_form": form,
            "page_obj": page_obj,
            "question_mode": question_mode,
            "search_page": force_questions,
        },
    )


def paper_list(request):
    return _listing_response(request)


def search(request):
    return _listing_response(request, force_questions=True)


def paper_detail(request, pk):
    paper = get_object_or_404(Paper, pk=pk, status=Paper.Status.PUBLISHED)
    questions = Question.objects.filter(
        paper=paper, status=Question.Status.PUBLISHED
    ).select_related("paper").prefetch_related("knowledge_points")
    return render(
        request,
        "question_bank/paper_detail.html",
        {"paper": paper, "questions": with_user_flags(questions, request.user)},
    )


def question_detail(request, pk):
    questions = Question.objects.filter(
        status=Question.Status.PUBLISHED,
        paper__status=Paper.Status.PUBLISHED,
    ).select_related("paper").prefetch_related("knowledge_points")
    question = get_object_or_404(with_user_flags(questions, request.user), pk=pk)
    siblings = Question.objects.filter(
        paper=question.paper, status=Question.Status.PUBLISHED
    )
    return render(
        request,
        "question_bank/question_detail.html",
        {
            "question": question,
            "previous_question": siblings.filter(sort_order__lt=question.sort_order).last(),
            "next_question": siblings.filter(sort_order__gt=question.sort_order).first(),
        },
    )


def not_found(request, exception):
    return render(request, "404.html", status=404)
