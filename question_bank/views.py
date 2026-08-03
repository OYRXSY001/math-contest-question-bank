from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import QuestionFilterForm
from .models import Favorite, Paper, Question, WrongQuestion
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


def _return_url(request, question):
    candidate = request.POST.get("next", "")
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return reverse("question-detail", args=[question.pk])


def _published_question(pk):
    return get_object_or_404(
        Question,
        pk=pk,
        status=Question.Status.PUBLISHED,
        paper__status=Paper.Status.PUBLISHED,
    )


@login_required
@require_POST
def favorite_add(request, pk):
    question = _published_question(pk)
    Favorite.objects.get_or_create(user=request.user, question=question)
    messages.success(request, "已加入收藏。")
    return redirect(_return_url(request, question))


@login_required
@require_POST
def favorite_remove(request, pk):
    question = _published_question(pk)
    Favorite.objects.filter(user=request.user, question=question).delete()
    messages.success(request, "已取消收藏。")
    return redirect(_return_url(request, question))


@login_required
@require_POST
def wrong_add(request, pk):
    question = _published_question(pk)
    WrongQuestion.objects.get_or_create(user=request.user, question=question)
    messages.success(request, "已加入错题本。")
    return redirect(_return_url(request, question))


@login_required
@require_POST
def wrong_remove(request, pk):
    question = _published_question(pk)
    WrongQuestion.objects.filter(user=request.user, question=question).delete()
    messages.success(request, "已移出错题本。")
    return redirect(_return_url(request, question))


def _personal_list(request, relation, template_name):
    base = Question.objects.filter(**{f"{relation}__user": request.user})
    questions, form = filtered_questions(request.GET, base_queryset=base)
    questions = with_user_flags(questions, request.user)
    page_obj = Paginator(questions, 20).get_page(request.GET.get("page"))
    return render(
        request,
        template_name,
        {"filter_form": form, "page_obj": page_obj, "clear_url": request.path},
    )


@login_required
def favorites(request):
    return _personal_list(request, "favorited_by", "question_bank/favorites.html")


@login_required
def wrong_questions(request):
    return _personal_list(request, "marked_wrong_by", "question_bank/wrong_questions.html")


def not_found(request, exception):
    return render(request, "404.html", status=404)
