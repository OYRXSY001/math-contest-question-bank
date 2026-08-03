from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("papers/", views.paper_list, name="paper-list"),
    path("papers/<int:pk>/", views.paper_detail, name="paper-detail"),
    path("questions/<int:pk>/", views.question_detail, name="question-detail"),
    path("search/", views.search, name="search"),
]
