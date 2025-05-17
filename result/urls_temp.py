from django.urls import path
from .views_temp import (
    add_score,
    add_score_for,
)


urlpatterns = [
    path("manage-score/", add_score, name="add_score"),
    path("manage-score/<int:id>/", add_score_for, name="add_score_for"),
] 