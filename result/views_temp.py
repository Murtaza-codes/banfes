from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import lecturer_required
from course.models import Course
from core.models import Session, Semester


@login_required
@lecturer_required
def add_score(request):
    """
    Shows a page where a lecturer will select a course allocated
    to him for score entry. in a specific semester and session
    """
    current_session = Session.objects.filter(is_current_session=True).first()
    
    if not current_session:
        return render(request, "result/add_score.html")
        
    current_semester = Semester.objects.filter(
        is_current_semester=True, session=current_session
    ).first()

    if not current_semester:
        return render(request, "result/add_score.html")

    courses = Course.objects.filter(
        allocated_course__lecturer__pk=request.user.id
    ).filter(semester=current_semester)
    context = {
        "current_session": current_session,
        "current_semester": current_semester,
        "courses": courses,
    }
    return render(request, "result/add_score.html", context)


def add_score_for(request, id):
    return render(request, "result/add_score_for.html") 