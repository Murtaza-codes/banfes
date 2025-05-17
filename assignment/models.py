from django.db import models
from django.conf import settings
from course.models import Course, Topic
import os
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


TYPE_CHOICES = [
    ('project', 'Project'),
    ('essay', 'Essay'),
    ('problem', 'Problem'),
]
STATUS_CHOICES = [
    ('open', 'Open'),
    ('hidden', 'Hidden'),
]


class Assignment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='assignments')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assignment_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='project',
        null=False,
        blank=False,
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='hidden',
        null=False,
        blank=False,
    )
    evaluation_criteria = models.FileField(
        upload_to='assignment/evaluation_files/', blank=False, null=False, max_length=255)
    deadline = models.DateTimeField(null=False, blank=False)
    allowed_submissions = models.IntegerField(default=1)
    additional_file = models.FileField(
        upload_to='assignment/additional_files/', blank=True, null=True,
        max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # Using DateTimeField
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('deadline',)

    def __str__(self):
        return self.title

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignment_submissions')
    attempts = models.PositiveIntegerField(default=0)
    extracted_text = models.TextField(null=True, blank=True)
    submission_text = models.TextField(blank=True, null=True)
    ai_score = models.FloatField(blank=True, null=True,
                                 validators=[MinValueValidator(0), MaxValueValidator(100)])
    teacher_score = models.FloatField(blank=True, null=True,
                                      validators=[MinValueValidator(0), MaxValueValidator(100)])
    final_score = models.FloatField(blank=True, null=True,
                                    validators=[MinValueValidator(0), MaxValueValidator(100)])
    ai_feedback = models.TextField(blank=True, null=True)
    teacher_feedback = models.TextField(blank=True, null=True)
    result_file = models.FileField(
        upload_to='assignment/results/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Using DateTimeField
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


class AssignmentSubmissionFile(models.Model):
    submission = models.ForeignKey(
        AssignmentSubmission, on_delete=models.CASCADE, related_name='submission_files')
    file = models.FileField(upload_to='assignment/submissions/files/', max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)  # Using DateTimeField
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return os.path.basename(self.file.name)
