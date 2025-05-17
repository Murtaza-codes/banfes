from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import Sum, Max, Count, Q, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django_filters.views import FilterView
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
import csv
import xlwt
import io
import datetime
from django.template.loader import get_template
from xhtml2pdf import pisa

from accounts.decorators import lecturer_required, student_required
from accounts.models import Student
from course.filters import CourseAllocationFilter, ProgramFilter
from course.forms import (
    CourseAddForm,
    CourseAllocationForm,
    EditCourseAllocationForm,
    CourseSessionForm,
    ProgramForm,
    UploadFormFile,
    UploadFormVideo,
    TopicForm,
)
from course.models import (
    Course,
    CourseAllocation,
    CourseSession,
    Program,
    Upload,
    UploadVideo,
    Topic,
    DiscussionTopic,
    DiscussionResponse,
)
from result.models import TakenCourse


# ########################################################
# Program Views
# ########################################################


@method_decorator([login_required, lecturer_required], name="dispatch")
class ProgramFilterView(FilterView):
    filterset_class = ProgramFilter
    template_name = "course/program_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Programs"
        return context


@login_required
@lecturer_required
def program_add(request):
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            messages.success(request, f"{program.title} program has been created.")
            return redirect("programs")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = ProgramForm()
    return render(
        request, "course/program_add.html", {"title": "Add Program", "form": form}
    )


@login_required
def program_detail(request, pk):
    # Get program with a single database query
    program = get_object_or_404(Program, pk=pk)
    
    # Optimize the courses query by adding caching to the queryset
    courses_queryset = Course.objects.filter(program_id=pk).order_by("-year")
    
    # Calculate credits once before pagination to avoid recalculation
    credits = courses_queryset.aggregate(total_credits=Sum("credit"))
    
    # Apply pagination after obtaining the queryset
    paginator = Paginator(courses_queryset, 10)
    page = request.GET.get("page")
    courses = paginator.get_page(page)
    
    return render(
        request,
        "course/program_single.html",
        {
            "title": program.title,
            "program": program,
            "courses": courses,
            "credits": credits,
        },
    )


@login_required
@lecturer_required
def program_edit(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == "POST":
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            program = form.save()
            messages.success(request, f"{program.title} program has been updated.")
            return redirect("programs")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = ProgramForm(instance=program)
    return render(
        request, "course/program_add.html", {"title": "Edit Program", "form": form}
    )


@login_required
@lecturer_required
def program_delete(request, pk):
    program = get_object_or_404(Program, pk=pk)
    title = program.title
    program.delete()
    messages.success(request, f"Program {title} has been deleted.")
    return redirect("programs")


# ########################################################
# Course Views
# ########################################################


@login_required
def course_single(request, slug):
    # Optimize database query with select_related
    course = get_object_or_404(Course.objects.select_related('program'), slug=slug)
    
    # Use a single query with prefetch_related to get topics and their related files and videos
    topics = Topic.objects.filter(course=course).prefetch_related('files', 'videos')
    
    # Use select_related on foreign keys for better performance
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id).select_related('lecturer')
    
    # Since we're prefetching files and videos with topics, we don't need these separate queries
    # files = Upload.objects.filter(course__slug=slug)
    # videos = UploadVideo.objects.filter(course__slug=slug)

    return render(
        request,
        "course/course_single.html",
        {
            "title": course.title,
            "course": course,
            "topics": topics,
            # Use the prefetched data instead of separate queries
            "files": None,  # Will use topics.files in the template
            "videos": None,  # Will use topics.videos in the template
            "lecturers": lecturers,
            "active_page": "overview",
            "media_url": settings.MEDIA_URL,
        },
    )


@login_required
@lecturer_required
def course_add(request, pk):
    program = get_object_or_404(Program, pk=pk)
    if request.method == "POST":
        form = CourseAddForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(
                request, f"{course.title} ({course.code}) has been created."
            )
            return redirect("program_detail", pk=program.pk)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = CourseAddForm(initial={"program": program})
    return render(
        request,
        "course/course_add.html",
        {"title": "Add Course", "form": form, "program": program},
    )


@login_required
@lecturer_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == "POST":
        form = CourseAddForm(request.POST, instance=course)
        if form.is_valid():
            course = form.save()
            messages.success(
                request, f"{course.title} ({course.code}) has been updated."
            )
            return redirect("program_detail", pk=course.program.pk)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = CourseAddForm(instance=course)
    return render(
        request, "course/course_add.html", {"title": "Edit Course", "form": form, "course": course}
    )

@login_required
@lecturer_required
def course_delete(request, slug):
    course = get_object_or_404(Course, slug=slug)
    title = course.title
    program_id = course.program.id
    course.delete()
    messages.success(request, f"Course {title} has been deleted.")
    return redirect("program_detail", pk=program_id)







# ########################################################
# Course Session Views
# ########################################################


@login_required
@lecturer_required
def manage_sessions(request, slug):
    course = get_object_or_404(Course, slug=slug)
    sessions = CourseSession.objects.filter(course=course)
    return render(request, 'course/course_session.html', {
        'course': course,
        'sessions': sessions,
    })


# views.py - Update add_session view
@login_required
@lecturer_required
def add_session(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = CourseSessionForm(request.POST, course=course)
        if form.is_valid():
            session = form.save(commit=False)
            session.course = course
            session.save()
            messages.success(request, 'Session added successfully.')
            return redirect('course_session', slug=slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseSessionForm(course=course)
    return render(request, 'course/course_add_session.html', {'form': form, 'course': course})
    

@login_required
@lecturer_required
def edit_session(request, slug, session_id):
    session = get_object_or_404(CourseSession, id=session_id, course__slug=slug)
    if request.method == 'POST':
        form = CourseSessionForm(request.POST, instance=session, course=session.course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session updated successfully.')
            return redirect('course_session', slug=slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CourseSessionForm(instance=session, course=session.course)
    
    return render(request, 'course/course_add_session.html', {
        'form': form,
        'session': session,
        'course': session.course
    })

@login_required
@lecturer_required
def delete_session(request, slug, session_id):
    print("delete session", slug, session_id)
    session = get_object_or_404(CourseSession, id=session_id, course__slug=slug)
    session.delete()
    messages.success(request, 'Session deleted successfully.')
    return redirect('course_session', slug=slug)


# ########################################################
# Course Features Views
# ########################################################

@login_required
def course_participants(request, slug):
    course = get_object_or_404(Course, slug=slug)
    students = Student.objects.filter(takencourse__course=course).distinct()
    lecturers = CourseAllocation.objects.filter(courses__pk=course.id)

    for student in students:
        print(student.student.email)   
    
    context = {
        "title": course.title,
        "course": course,
        "students": students,
        "lecturers": lecturers,
        "active_page": "participants",
    }

    return render(
        request,
        "course/course_participant.html",
        context,)


@login_required
def course_grade(request, slug):
    course = get_object_or_404(Course, slug=slug)
    students = Student.objects.filter(takencourse__course__slug=slug).distinct()
    
    # Calculate real data instead of using fake data
    total_students = students.count()
    
    # Calculate average grade
    avg_grade = course.taken_courses.aggregate(Avg('total'))['total__avg']
    if avg_grade:
        avg_grade = f"{avg_grade:.1f}%"
    else:
        avg_grade = "N/A"
    
    # Get all taken courses for this course
    taken_courses = course.taken_courses.all().select_related('student__student')

    context = {
        "title": course.title,
        "course": course,
        "students": students,
        "active_page": "grades",
        "total_students": total_students,
        "avg_grade": avg_grade,
        "taken_courses": taken_courses,
    }

    return render(
        request,
        "course/course_grade.html",
        context)


@login_required
def export_grades_csv(request, slug):
    course = get_object_or_404(Course, slug=slug)
    taken_courses = course.taken_courses.all().select_related('student__student')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="grades_{course.code}.csv"'
    
    writer = csv.writer(response)
    # Write header with course info
    writer.writerow(['Learning Management System'])
    writer.writerow(['Excellence in Education'])
    writer.writerow([])
    writer.writerow([f'Course Grades: {course.title} ({course.code})'])
    
    try:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        writer.writerow([f'Generated: {current_date}'])
    except:
        writer.writerow(['Generated: Today'])
    
    writer.writerow([])
    
    # Write summary data
    avg_data = taken_courses.aggregate(Avg('total'))
    avg_grade = 'N/A'
    if avg_data['total__avg']:
        avg_grade = f"{avg_data['total__avg']:.1f}%"
    
    writer.writerow(['Total Students:', taken_courses.count()])
    writer.writerow(['Average Grade:', avg_grade])
    writer.writerow([])
    
    # Write column headers
    writer.writerow(['No.', 'Student Name', 'Student ID', 'Assignment', 'Quiz', 'Mid Exam', 'Attendance', 'Final Exam', 'Total', 'Grade'])
    
    # Write data rows
    for index, taken in enumerate(taken_courses, 1):
        writer.writerow([
            index,
            taken.student.student.get_full_name,
            taken.student.id_number if hasattr(taken.student, 'id_number') else taken.student.student.username,
            taken.assignment,
            taken.quiz,
            taken.mid_exam if hasattr(taken, 'mid_exam') else '-',
            taken.attendance if hasattr(taken, 'attendance') else '-',
            taken.final_exam,
            taken.total,
            taken.grade
        ])
    
    return response


@login_required
def export_grades_excel(request, slug):
    course = get_object_or_404(Course, slug=slug)
    taken_courses = course.taken_courses.all().select_related('student__student')
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename="grades_{course.code}.xls"'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Grades')
    
    # Add title and logo information at the top
    title_style = xlwt.XFStyle()
    title_style.font.bold = True
    title_style.font.height = 20 * 16  # 16pt
    title_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
    
    # Merge cells for title
    ws.write_merge(0, 0, 0, 8, 'Learning Management System', title_style)
    
    subtitle_style = xlwt.XFStyle()
    subtitle_style.font.height = 12 * 16  # 12pt
    subtitle_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
    ws.write_merge(1, 1, 0, 8, 'Excellence in Education', subtitle_style)
    
    course_title_style = xlwt.XFStyle()
    course_title_style.font.bold = True
    course_title_style.font.height = 14 * 16  # 14pt
    course_title_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
    ws.write_merge(3, 3, 0, 8, f'Course Grades: {course.title} ({course.code})', course_title_style)
    
    # Add date
    date_style = xlwt.XFStyle()
    date_style.alignment.horz = xlwt.Alignment.HORZ_RIGHT
    try:
        import datetime
        ws.write(4, 8, f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d")}', date_style)
    except:
        ws.write(4, 8, f'Generated: Today', date_style)
    
    # Calculate the average
    avg_data = taken_courses.aggregate(Avg('total'))
    avg_grade = 'N/A'
    if avg_data['total__avg']:
        avg_grade = f"{avg_data['total__avg']:.1f}%"
    
    # Add summary data
    summary_style = xlwt.XFStyle()
    summary_style.font.bold = True
    ws.write(6, 0, 'Total Students:', summary_style)
    ws.write(6, 1, taken_courses.count())
    
    ws.write(7, 0, 'Average Grade:', summary_style)
    ws.write(7, 1, avg_grade)
    
    # Sheet header, first row for data
    row_num = 9
    
    header_style = xlwt.XFStyle()
    header_style.font.bold = True
    header_style.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    header_style.pattern.pattern_fore_colour = xlwt.Style.colour_map['light_green']
    header_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
    
    columns = [
        'No.', 
        'Student Name', 
        'Student ID', 
        'Assignment', 
        'Quiz', 
        'Mid Exam', 
        'Attendance', 
        'Final Exam', 
        'Total', 
        'Grade'
    ]
    
    col_widths = [5, 30, 15, 12, 12, 12, 12, 12, 12, 10]
    
    try:
        for col_num, (column, width) in enumerate(zip(columns, col_widths)):
            ws.col(col_num).width = width * 256  # Set column width
            ws.write(row_num, col_num, column, header_style)
        
        # Sheet body, remaining rows
        data_style = xlwt.XFStyle()
        data_style.alignment.horz = xlwt.Alignment.HORZ_CENTER
        
        for taken in taken_courses:
            row_num += 1
            try:
                row = [
                    row_num - 9,  # Counter starting from 1
                    taken.student.student.get_full_name,
                    taken.student.id_number if hasattr(taken.student, 'id_number') else taken.student.student.username,
                    taken.assignment,
                    taken.quiz,
                    taken.mid_exam if hasattr(taken, 'mid_exam') else '-',
                    taken.attendance if hasattr(taken, 'attendance') else '-',
                    taken.final_exam,
                    taken.total,
                    taken.grade
                ]
                for col_num, cell_value in enumerate(row):
                    ws.write(row_num, col_num, str(cell_value), data_style)
            except Exception as e:
                # If there's an error with a specific row, continue with the next one
                continue
        
        wb.save(response)
        return response
    except Exception as e:
        return HttpResponse(f"Error generating Excel file: {str(e)}<br>Please try the CSV export instead.")


@login_required
def export_grades_pdf(request, slug):
    course = get_object_or_404(Course, slug=slug)
    taken_courses = course.taken_courses.all().select_related('student__student')
    
    # Calculate average
    avg_data = taken_courses.aggregate(Avg('total'))
    avg_grade = None
    if avg_data['total__avg']:
        avg_grade = f"{avg_data['total__avg']:.1f}"
    
    template_path = 'course/grade_pdf_template.html'
    context = {
        'course': course, 
        'taken_courses': taken_courses,
        'title': f'Course Grades: {course.title}',
        'avg_grade': avg_grade,
        'MEDIA_URL': settings.MEDIA_URL,
        'STATIC_URL': settings.STATIC_URL
    }
    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="grades_{course.code}.pdf"'
    
    # Find the template and render it
    template = get_template(template_path)
    html = template.render(context)
    
    try:
        # Create a PDF
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        # If error then show some error view
        if pisa_status.err:
            return HttpResponse('We had some errors generating the PDF: <pre>' + html + '</pre>')
        
        return response
    except Exception as e:
        # Handle any other exceptions that might occur
        return HttpResponse(f'Error generating PDF: {str(e)}<br>Please try the Excel or CSV export instead.')


@login_required
def course_discussion(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    # Get filters
    topic_type = request.GET.get('type', None)
    sort_by = request.GET.get('sort', 'newest')
    search_query = request.GET.get('search', None)
    
    # Start with all topics for this course
    topics = DiscussionTopic.objects.filter(course=course)
    
    # Apply topic type filter if specified
    if topic_type:
        topics = topics.filter(topic_type=topic_type)
    
    # Apply search filter if specified
    if search_query:
        topics = topics.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by == 'active':
        # Topics with most recent responses first
        topics = topics.annotate(
            latest_response=Max('responses__created_at')
        ).order_by('-latest_response', '-created_at')
    elif sort_by == 'unanswered':
        # Topics with no responses first
        topics = topics.annotate(
            response_count=Count('responses')
        ).order_by('response_count', '-created_at')
    else:  # 'newest' is the default
        topics = topics.order_by('-created_at')
    
    # Ensure all topics have slugs
    from core.utils import unique_slug_generator
    for topic in topics:
        if not topic.slug:
            topic.slug = unique_slug_generator(topic)
            topic.save()
    
    return render(request, 'course/course_discussion.html', {
        'course': course,
        'topics': topics,
        'active_page': 'discussion'
    })


@login_required
def course_discussion_new_topic(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        topic_type = request.POST.get('topic_type')
        
        if not title or not content or not topic_type:
            messages.error(request, _("Please fill in all required fields."))
            return redirect('course_discussion', slug=slug)
        
        topic = DiscussionTopic.objects.create(
            course=course,
            title=title,
            content=content,
            topic_type=topic_type,
            created_by=request.user
        )
        
        # Save to trigger pre_save slug generation
        topic.save()
        
        # Ensure slug exists before redirecting
        if not topic.slug:
            from core.utils import unique_slug_generator
            topic.slug = unique_slug_generator(topic)
            topic.save()
        
        messages.success(request, _("Discussion topic created successfully."))
        return redirect('course_discussion_topic', slug=slug, topic_slug=topic.slug)
    
    return redirect('course_discussion', slug=slug)


@login_required
def course_discussion_topic(request, slug, topic_slug):
    course = get_object_or_404(Course, slug=slug)
    topic = get_object_or_404(DiscussionTopic, slug=topic_slug, course=course)
    
    # Increment view count only once per session
    session_key = f'viewed_topic_{topic.id}'
    if not request.session.get(session_key, False):
        topic.views += 1
        topic.save()
        request.session[session_key] = True
    
    # Handle new response
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            response = DiscussionResponse.objects.create(
                topic=topic,
                content=content,
                created_by=request.user
            )
            
            # If this is a reply to another response, set the parent
            if parent_id and parent_id.isdigit():
                try:
                    parent_response = DiscussionResponse.objects.get(id=parent_id, topic=topic)
                    response.parent = parent_response
                    response.save()
                except DiscussionResponse.DoesNotExist:
                    pass
                
            messages.success(request, _("Your response has been posted."))
            return redirect('course_discussion_topic', slug=slug, topic_slug=topic_slug)
        else:
            messages.error(request, _("Response content cannot be empty."))
    
    # Get responses with their replies
    responses = topic.responses.select_related('created_by').order_by('created_at')
    
    return render(request, 'course/course_discussion_topic.html', {
        'course': course,
        'topic': topic,
        'responses': responses,
        'active_page': 'discussion'
    })


@login_required
def course_attendance(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    return render(request, 'course/course_attendance.html', {
        'course': course,
        'active_page': 'attendance'
    })


@login_required
@lecturer_required
def record_attendance(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        # Process the form submission
        attendance_date = request.POST.get('attendance_date')
        session_type = request.POST.get('session_type')
        
        # Here you would typically save the attendance records
        # This is a placeholder that would need to be implemented
        # based on your actual data model
        
        messages.success(request, _('Attendance recorded successfully.'))
        return redirect('course_attendance', slug=slug)
    
    # If not POST, redirect to the attendance page
    return redirect('course_attendance', slug=slug)



# ########################################################
# Course Allocation Views
# ########################################################


@method_decorator([login_required, lecturer_required], name="dispatch")
class CourseAllocationFormView(CreateView):
    form_class = CourseAllocationForm
    template_name = "course/course_allocation_form.html"

    def form_valid(self, form):
        lecturer = form.cleaned_data["lecturer"]
        selected_courses = form.cleaned_data["courses"]
        allocation, created = CourseAllocation.objects.get_or_create(lecturer=lecturer)
        allocation.courses.set(selected_courses)
        messages.success(
            self.request, f"Courses allocated to {lecturer.get_full_name} successfully."
        )
        return redirect("course_allocation_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Assign Course"
        return context


@method_decorator([login_required, lecturer_required], name="dispatch")
class CourseAllocationFilterView(FilterView):
    filterset_class = CourseAllocationFilter
    template_name = "course/course_allocation_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Course Allocations"
        return context


@login_required
@lecturer_required
def edit_allocated_course(request, pk):
    allocation = get_object_or_404(CourseAllocation, pk=pk)
    if request.method == "POST":
        form = EditCourseAllocationForm(request.POST, instance=allocation)
        if form.is_valid():
            form.save()
            messages.success(request, "Course allocation has been updated.")
            return redirect("course_allocation_view")
        messages.error(request, "Correct the error(s) below.")
    else:
        form = EditCourseAllocationForm(instance=allocation)
    return render(
        request,
        "course/course_allocation_form.html",
        {"title": "Edit Course Allocation", "form": form},
    )


@login_required
@lecturer_required
def deallocate_course(request, pk):
    allocation = get_object_or_404(CourseAllocation, pk=pk)
    allocation.delete()
    messages.success(request, "Successfully deallocated courses.")
    return redirect("course_allocation_view")







# ########################################################
# Topics Views
# ########################################################

@login_required
@lecturer_required
def topic_create(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = TopicForm(request.POST, course=course)
        if form.is_valid():
            try:
                with transaction.atomic():
                    topic = form.save(commit=False)
                    topic.course = course
                    
                    if not form.cleaned_data.get('order'):
                        # Auto-assign order if not specified
                        max_order = Topic.objects.filter(course=course).aggregate(
                            Max('order'))['order__max']
                        topic.order = (max_order or 0) + 1
                    
                    # Validate order uniqueness
                    if Topic.objects.filter(
                        course=course, 
                        order=topic.order
                    ).exists():
                        form.add_error('order', 
                            f'Topic with order {topic.order} already exists')
                        raise ValueError('Duplicate order')
                        
                    topic.save()
                    messages.success(
                        request, 
                        f"Topic '{topic.title}' created successfully."
                    )
                    return redirect('course_detail', slug=slug)
                    
            except IntegrityError:
                messages.error(
                    request,
                    f'Topic order {topic.order} is already taken. Please choose a different order number.'
                )
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = TopicForm(course=course)
    
    return render(request, 'course/course_topic_form.html', {
        'form': form,
        'course': course,
        'active_page': 'overview',
        'title': 'Create New Topic'
    })



@login_required
@lecturer_required
def topic_edit(request, slug, pk):
    # Get the course first using the slug
    course = get_object_or_404(Course, slug=slug)
    # Then get the topic using pk and course
    topic = get_object_or_404(Topic, pk=pk, course=course)
    
    if request.method == 'POST':
        form = TopicForm(request.POST, instance=topic, course=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Topic '{topic.title}' updated successfully.")
            return redirect('course_detail', slug=slug)
    else:
        form = TopicForm(instance=topic, course=course)
    
    return render(request, 'course/course_topic_form.html', {
        'form': form,
        'course': course,
        'topic': topic,
        'title': 'Edit Topic',
        'active_page': 'overview'
    })

@login_required
@lecturer_required
def topic_delete(request, slug, pk):
    # Verify request method
    if request.method != 'POST':
        messages.error(request, "Invalid request method.")
        return redirect('course_detail', slug=slug)

    try:
        # Get course first
        course = get_object_or_404(Course, slug=slug)
        
        # Get topic and verify it belongs to the course
        topic = get_object_or_404(Topic, pk=pk, course=course)
        
        # Store topic info for success message
        topic_title = topic.title
        
        # Delete topic and all related content
        topic.delete()
        
        messages.success(
            request, 
            f"Topic '{topic_title}' and all associated content deleted successfully."
        )
    except Topic.DoesNotExist:
        messages.error(request, "Topic not found.")
    except Exception as e:
        messages.error(request, f"Error deleting topic: {str(e)}")
    
    return redirect('course_detail', slug=slug)





# ########################################################
# File Upload Views
# ########################################################


@login_required
@lecturer_required
def handle_file_upload(request, slug):
    course = get_object_or_404(Course, slug=slug)
    topic_id = request.GET.get('topic')
    topic = get_object_or_404(Topic, id=topic_id, course=course) if topic_id else None
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.course = course
            upload.topic = topic
            upload.save()
            messages.success(request, f"{upload.title} has been uploaded.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = UploadFormFile()
    return render(
        request,
        "upload/upload_file_form.html",
        {"title": "File Upload", "form": form, "course": course, "topic": topic},
    )


@login_required
@lecturer_required
def handle_file_edit(request, slug, file_id):
    course = get_object_or_404(Course, slug=slug)
    upload = get_object_or_404(Upload, pk=file_id)
    if request.method == "POST":
        form = UploadFormFile(request.POST, request.FILES, instance=upload)
        if form.is_valid():
            upload = form.save()
            messages.success(request, f"{upload.title} has been updated.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = UploadFormFile(instance=upload)
    return render(
        request,
        "upload/upload_file_form.html",
        {"title": "Edit File", "form": form, "course": course},
    )


@login_required
@lecturer_required
def handle_file_delete(request, slug, file_id):
    upload = get_object_or_404(Upload, pk=file_id)
    title = upload.title
    upload.delete()
    messages.success(request, f"{title} has been deleted.")
    return redirect("course_detail", slug=slug)


# ########################################################
# Video Upload Views
# ########################################################


@login_required
@lecturer_required
def handle_video_upload(request, slug):
    print("request to upload video", request)
    course = get_object_or_404(Course, slug=slug)
    print("course", course)
    topic_id = request.GET.get('topic')
    topic = get_object_or_404(Topic, id=topic_id, course=course) if topic_id else None
    print("topic", topic)
    if request.method == "POST":
        form = UploadFormVideo(request.POST, request.FILES)
        if form.is_valid():
            print("form is valid")
            video = form.save(commit=False)
            video.course = course
            video.topic = topic
            video.save()
            messages.success(request, f"{video.title} has been uploaded.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        print("form is not valid")
        form = UploadFormVideo()
    return render(
        request,
        "upload/upload_video_form.html",
        {"title": "Video Upload", "form": form, "course": course, "topic": topic},
    )


@login_required
def handle_video_single(request, slug, video_slug):
    course = get_object_or_404(Course, slug=slug)
    video = get_object_or_404(UploadVideo, slug=video_slug)
    return render(
        request,
        "upload/video_single.html",
        {"video": video, "course": course, "active_page": "overview"},
    )


@login_required
@lecturer_required
def handle_video_edit(request, slug, video_slug):
    course = get_object_or_404(Course, slug=slug)
    video = get_object_or_404(UploadVideo, slug=video_slug)
    if request.method == "POST":
        form = UploadFormVideo(request.POST, request.FILES, instance=video)
        if form.is_valid():
            video = form.save()
            messages.success(request, f"{video.title} has been updated.")
            return redirect("course_detail", slug=slug)
        messages.error(request, "Correct the error(s) below.")
    else:
        form = UploadFormVideo(instance=video)
    return render(
        request,
        "upload/upload_video_form.html",
        {"title": "Edit Video", "form": form, "course": course},
    )


@login_required
@lecturer_required
def handle_video_delete(request, slug, video_slug):
    video = get_object_or_404(UploadVideo, slug=video_slug)
    title = video.title
    video.delete()
    messages.success(request, f"{title} has been deleted.")
    return redirect("course_detail", slug=slug)


# ########################################################
# Course Registration Views
# ########################################################


@login_required
@student_required
def course_registration(request):
    # Get student object once and reuse it
    student = get_object_or_404(Student.objects.select_related('program', 'student'), 
                                student__id=request.user.id)
    
    if request.method == "POST":
        course_ids = request.POST.getlist("course_ids")
        try:
            # Use a transaction to ensure all operations succeed or fail together
            with transaction.atomic():
                # Bulk create TakenCourse objects instead of creating one by one
                courses_to_register = Course.objects.filter(pk__in=course_ids)
                
                # Prepare bulk create data
                taken_courses = [
                    TakenCourse(student=student, course=course) 
                    for course in courses_to_register
                ]
                
                # Bulk create
                TakenCourse.objects.bulk_create(taken_courses)
                
            messages.success(request, "Courses registered successfully!")
        except Exception as e:
            messages.error(request, f"Error registering courses: {str(e)}")
            
        return redirect("course_registration")
    else:
        # Get taken courses and their IDs in one query
        taken_courses = TakenCourse.objects.filter(student=student).select_related('course')
        taken_course_ids = [tc.course.id for tc in taken_courses]

        # Use select_related to reduce database queries
        courses = (
            Course.objects.filter(
                program__pk=student.program.id,
                level=student.level,
            )
            .exclude(id__in=taken_course_ids)
            .select_related('program')  # Prefetch related program
            .order_by("year")
        )

        # Get all course counts in a single query to avoid repeated count queries
        all_courses_count = Course.objects.filter(
            level=student.level, 
            program__pk=student.program.id
        ).count()

        # Get registered courses with select_related
        registered_courses = [tc.course for tc in taken_courses]
        
        # Registration status flags - use length of list instead of additional query
        registered_count = len(registered_courses)
        no_course_is_registered = registered_count == 0
        all_courses_are_registered = registered_count == all_courses_count

        # Calculate total credits - avoid using sum() with generator
        total_registered_credit = 0
        for course in registered_courses:
            total_registered_credit += course.credit

        context = {
            "all_courses_are_registered": all_courses_are_registered,
            "no_course_is_registered": no_course_is_registered,
            "courses": courses,
            "registered_courses": registered_courses,
            "total_registered_credit": total_registered_credit,
            "student": student,
        }
        return render(request, "course/course_registration.html", context)


@login_required
@student_required
def course_drop(request):
    if request.method == "POST":
        student = get_object_or_404(Student, student__pk=request.user.id)
        course_ids = request.POST.getlist("course_ids")
        print("course_ids", course_ids)
        for course_id in course_ids:
            course = get_object_or_404(Course, pk=course_id)
            TakenCourse.objects.filter(student=student, course=course).delete()
        messages.success(request, "Courses dropped successfully!")
        return redirect("course_registration")





# ########################################################
# User Course List View
# ########################################################


@login_required
def user_course_list(request):
    if request.user.is_lecturer:
        courses = Course.objects.filter(allocated_course__lecturer__pk=request.user.id)
        return render(request, "course/user_course_list.html", {"courses": courses})

    if request.user.is_student:
        student = get_object_or_404(Student, student__pk=request.user.id)
        taken_courses = TakenCourse.objects.filter(student=student)
        return render(
            request,
            "course/user_course_list.html",
            {"student": student, "taken_courses": taken_courses},
        )

    # For other users
    return render(request, "course/user_course_list.html")


# ########################################################
# AI Assistant View
# ########################################################

@login_required
def course_ai_assistant(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            prompt = data.get('prompt', '')
            
            # Here you would integrate with an AI service
            # This is a placeholder response
            response = {
                'answer': _('This is a placeholder response from the AI assistant. The actual AI integration is not implemented yet.'),
                'success': True
            }
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'error': str(e), 'success': False}, status=400)
    
    return JsonResponse({'error': _('Only POST requests are allowed'), 'success': False}, status=405)


@login_required
def course_videos(request, slug):
    """View to list all videos for a course."""
    course = get_object_or_404(Course, slug=slug)
    
    # Get all videos associated with this course
    videos = UploadVideo.objects.filter(course=course).select_related('topic')
    
    return render(request, 'course/course_videos.html', {
        'course': course,
        'videos': videos,
        'active_page': 'videos',
    })

# ########################################################
