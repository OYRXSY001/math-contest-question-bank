from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("papers/", views.paper_list, name="paper-list"),
    path("papers/<int:pk>/", views.paper_detail, name="paper-detail"),
    path("questions/<int:pk>/", views.question_detail, name="question-detail"),
    path("questions/<int:pk>/favorite/add/", views.favorite_add, name="favorite-add"),
    path("questions/<int:pk>/favorite/remove/", views.favorite_remove, name="favorite-remove"),
    path("questions/<int:pk>/wrong/add/", views.wrong_add, name="wrong-add"),
    path("questions/<int:pk>/wrong/remove/", views.wrong_remove, name="wrong-remove"),
    path("me/favorites/", views.favorites, name="favorites"),
    path("me/wrong-questions/", views.wrong_questions, name="wrong-questions"),
    path("search/", views.search, name="search"),
]
