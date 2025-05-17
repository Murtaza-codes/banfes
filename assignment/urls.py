from django.urls import path
from .views import (
    assignment_create_view,
    assignment_update_view,
    assignment_list,
    assignment_result,
    assignment_submission,
    assignment_submissions,
    assignment_submission_detail,
    assignment_delete,
    ajax_upload_file,
    ajax_delete_file,
    assignment_back
)

urlpatterns = [
    path('<slug>/assignment/', assignment_list, name='assignment_list'),
    path('course/<slug:slug>/assignment/add/',
         assignment_create_view, name='assignment_create'),
    path('course/<slug:slug>/assignment/<int:pk>/edit/',
         assignment_update_view, name='assignment_update'),
    path('<slug>/assignment/<int:assignment_id>/submit/',
         assignment_submission, name='assignment_submission'),
    path('assignment/<slug:slug>/assignment/<int:assignment_id>/back/',
         assignment_back, name='assignment_back'),
    path('<slug>/assignment/<int:assignment_id>/result/',
         assignment_result, name='assignment_result'),
    path('<slug>/assignment/<int:assignment_id>/submissions/',
         assignment_submissions, name='assignment_submissions'),
    path('<slug>/assignment/<int:assignment_id>/submissions/<int:submission_id>/',
         assignment_submission_detail, name='assignment_submission_detail'),
    path('<slug>/assignment/<int:pk>/delete/',
         assignment_delete, name='assignment_delete'),
    path('ajax/upload-file/', ajax_upload_file, name='ajax_upload_file'),
    path('ajax/delete-file/', ajax_delete_file, name='ajax_delete_file'),
]
