# Lecturer Dashboard

This document describes the Lecturer Dashboard functionality in the educational portal.

## Overview

The Lecturer Dashboard provides a centralized interface for lecturers to access and manage all their teaching-related activities. It presents all lecturer permissions as an intuitive grid of buttons with icons.

## Features

The dashboard provides quick access to the following lecturer functions:

1. **Course Management**
   - View and manage teaching sessions
   - Access course materials

2. **Student Scores**
   - Enter and update student scores
   - Manage assessment results

3. **Course Allocations**
   - View courses allocated to the lecturer
   - See current semester allocations

4. **Assignments & Quizzes**
   - Create and manage assignments
   - Monitor quiz progress

5. **Semester Management**
   - View active semesters
   - Access semester-specific information

6. **Profile Settings**
   - Update personal profile information
   - Change account settings

## Implementation

The dashboard is implemented with:
- Bootstrap 5 grid layout for responsive design
- Bootstrap Icons for clear visual indicators
- Full RTL (Right-to-Left) support for Farsi language
- Internationalization (i18n) support

## Access

Lecturers can access the dashboard via:
1. The main navigation dropdown menu
2. Direct URL at `/accounts/lecturer/dashboard/`

## Language Support

The dashboard fully supports multiple languages including:
- English (default)
- Farsi (RTL layout)

Language can be changed using the language switcher in the navigation bar.

## Technical Details

- View: `lecturer_dashboard` in `accounts/views.py`
- Template: `templates/lecturer/dashboard.html`
- URL pattern: Added to `accounts/urls.py`
- Translations: Added to `locale/fa/LC_MESSAGES/django.po` 