from django.urls import path
from . import views


urlpatterns = [
    # Program urls
    path("", views.ProgramFilterView.as_view(), name="programs"),
    path("<int:pk>/detail/", views.program_detail, name="program_detail"),
    path("add/", views.program_add, name="add_program"),
    path("<int:pk>/edit/", views.program_edit, name="edit_program"),
    path("<int:pk>/delete/", views.program_delete, name="program_delete"),
    # Course urls
    path("course/<slug>/detail/", views.course_single, name="course_detail"),
    path("<int:pk>/course/add/", views.course_add, name="course_add"),
    path("course/<slug>/edit/", views.course_edit, name="edit_course"),
    path("course/delete/<slug>/", views.course_delete, name="delete_course"),
    # CourseAllocation urls
    path(
        "course/assign/",
        views.CourseAllocationFormView.as_view(),
        name="course_allocation",
    ),
    path(
        "course/allocated/",
        views.CourseAllocationFilterView.as_view(),
        name="course_allocation_view",
    ),
    path(
        "allocated_course/<int:pk>/edit/",
        views.edit_allocated_course,
        name="edit_allocated_course",
    ),
    path(
        "course/<int:pk>/deallocate/", views.deallocate_course, name="course_deallocate"
    ),
    # Grade export urls
    path("course/<slug>/export/excel/", views.export_grades_excel, name="export_grades_excel"),
    path("course/<slug>/export/pdf/", views.export_grades_pdf, name="export_grades_pdf"),
    path("course/<slug>/export/csv/", views.export_grades_csv, name="export_grades_csv"),
    # File uploads urls
    path(
        "course/<slug>/documentations/upload/",
        views.handle_file_upload,
        name="upload_file_view",
    ),
    path(
        "course/<slug>/documentations/<int:file_id>/edit/",
        views.handle_file_edit,
        name="upload_file_edit",
    ),
    path(
        "course/<slug>/documentations/<int:file_id>/delete/",
        views.handle_file_delete,
        name="upload_file_delete",
    ),
    # Video uploads urls
    path(
        "course/<slug>/video_tutorials/upload/",
        views.handle_video_upload,
        name="upload_video",
    ),
    path(
        "course/<slug>/video_tutorials/<video_slug>/detail/",
        views.handle_video_single,
        name="video_single",
    ),
    path(
        "course/<slug>/video_tutorials/<video_slug>/edit/",
        views.handle_video_edit,
        name="upload_video_edit",
    ),
    path(
        "course/<slug>/video_tutorials/<video_slug>/delete/",
        views.handle_video_delete,
        name="upload_video_delete",
    ),
    # course registration
    path("course/registration/", views.course_registration, name="course_registration"),
    path("course/drop/", views.course_drop, name="course_drop"),
    path("my_courses/", views.user_course_list, name="user_course_list"),
    path(
        "course/<slug>/topics/create/",
        views.topic_create,
        name="topic_create"
    ),
    path(
        "course/<slug>/topics/<int:pk>/edit/",
        views.topic_edit,
        name="topic_edit"
    ),
    path(
        "course/<slug>/topics/<int:pk>/delete/",
        views.topic_delete,
        name="topic_delete"
    ),
    # course sub pages
    path("course/<slug>/participants/", views.course_participants, name="course_participants"),
    path("course/<slug>/attendance/", views.course_attendance, name="course_attendance"),
    path("course/<slug>/attendance/record/", views.record_attendance, name="record_attendance"),
    path("course/<slug>/course_discussion/", views.course_discussion, name='course_discussion'),
    path("course/<slug>/course_discussion/new/", views.course_discussion_new_topic, name='course_discussion_new_topic'),
    path("course/<slug>/course_discussion/<slug:topic_slug>/", views.course_discussion_topic, name='course_discussion_topic'),
    path("course/<slug>/grade/", views.course_grade, name="course_grade"),
    # AI assistant URL
    path("course/<slug>/ai_assistant/", views.course_ai_assistant, name="course_ai_assistant"),
    # Video list URL
    path("course/<slug>/videos/", views.course_videos, name="course_videos"),
    # session urls
    path('course/<slug>/sessions/', views.manage_sessions, name='course_session'),
    path('course/<slug>/sessions/add/', views.add_session, name='add_session'),
    path('course/<slug:slug>/sessions/<int:session_id>/edit/', views.edit_session, name='edit_session'),
    path('course/<slug:slug>/sessions/<int:session_id>/delete/', views.delete_session, name='delete_session'),
]
