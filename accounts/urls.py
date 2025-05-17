from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

# Removed app_name to avoid namespace issues with login/logout URLs

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.profile_single, name='profile_single'),
    
    # Dashboard URLs
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('lecturer/dashboard/', views.lecturer_dashboard, name='lecturer_dashboard'),
    
    # Admin URLs
    path('admin/panel/', views.admin_panel, name='admin_panel'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('password/change/', views.change_password, name='change_password'),
    
    # Password Reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # User Management URLs
    path('student/list/', views.StudentListView.as_view(), name='student_list'),
    path('lecturer/list/', views.LecturerFilterView.as_view(), name='lecturer_list'),
    
    # PDF Exports
    path('student/list/pdf/', views.render_student_pdf_list, name='student_list_pdf'),
    path('lecturer/list/pdf/', views.render_lecturer_pdf_list, name='lecturer_list_pdf'),
    
    # Staff Management
    path('staff/add/', views.staff_add_view, name='staff_add'),
    path('staff/<int:pk>/edit/', views.edit_staff, name='staff_edit'),
    path('staff/<int:pk>/delete/', views.delete_staff, name='staff_delete'),
    
    # Add the missing URL pattern for 'add_lecturer'
    path('lecturer/add/', views.staff_add_view, name='add_lecturer'),
    path('lecturer/<int:pk>/delete/', views.delete_staff, name='lecturer_delete'),
    
    # Student Management
    path('student/add/', views.student_add_view, name='student_add'),
    path('student/<int:pk>/edit/', views.edit_student, name='student_edit'),
    path('student/<int:pk>/delete/', views.delete_student, name='student_delete'),
    path('student/<int:pk>/program/edit/', views.edit_student_program, name='edit_student_program'),
]
