from django.contrib import admin

from .models import (
    Favorite,
    KnowledgePoint,
    Paper,
    Question,
    QuestionKnowledgePoint,
    WrongQuestion,
)


class QuestionKnowledgeInline(admin.TabularInline):
    model = QuestionKnowledgePoint
    extra = 0


@admin.register(Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ("edition", "stage", "original_category_label", "status")
    list_filter = ("edition", "stage", "status")
    search_fields = ("title", "original_category_label")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("paper", "question_no", "question_type", "status")
    list_filter = ("paper__edition", "paper__stage", "question_type", "status")
    search_fields = ("stem_md", "answer_md", "solution_md")
    inlines = (QuestionKnowledgeInline,)


@admin.register(KnowledgePoint)
class KnowledgePointAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "parent", "sort_order")
    list_filter = ("subject",)
    search_fields = ("name", "slug")


admin.site.register(Favorite)
admin.site.register(WrongQuestion)
