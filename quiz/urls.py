# quiz/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("<slug>/quizzes/", views.quiz_list, name="quiz_index"),
    path("progress/", view=views.QuizUserProgressView.as_view(), name="quiz_progress"),
    path("marking_list/", view=views.QuizMarkingList.as_view(), name="quiz_marking"),
    path("marking/<int:pk>/", view=views.QuizMarkingDetail.as_view(), name="quiz_marking_detail"),
    path("<int:pk>/<slug>/take/", view=views.QuizTake.as_view(), name="quiz_take"),
    path("<slug>/quiz_add/", views.QuizCreateView.as_view(), name="quiz_create"),
    path("<slug>/<int:pk>/add/", views.QuizUpdateView.as_view(), name="quiz_update"),
    path("<slug>/<int:pk>/delete/", views.quiz_delete, name="quiz_delete"),
    path("mc-question/add/<slug>/<int:quiz_id>/", views.MCQuestionCreate.as_view(), name="mc_create"),
    path("fix-records/", views.fix_quiz_records_view, name="fix_quiz_records"),
]
