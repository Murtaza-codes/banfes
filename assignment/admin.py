from django.contrib import admin
from .models import Assignment, AssignmentSubmission, AssignmentSubmissionFile
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from modeltranslation.forms import TranslationModelForm


class AssignmentSubmissionFileInline(admin.TabularInline):
    model = AssignmentSubmissionFile
    extra = 1


class AssignmentAdminForm(TranslationModelForm):
    class Meta:
        model = Assignment
        fields = [
            'title',
            'description',
            'assignment_type',
            'status',
            'deadline',
            'allowed_submissions',
            'additional_file',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            for field in ['title', 'description']:
                for lang_code in ['en', 'fa']:
                    trans_field = f"{field}_{lang_code}"
                    if trans_field in self.fields:
                        self.fields[trans_field].widget.attrs['readonly'] = True


class AssignmentAdmin(TranslationAdmin):
    list_display = (
        'id',
        'course',
        'title',
        'assignment_type',
        'status',
        'deadline',
        'allowed_submissions',
        'evaluation_criteria',
        'created_at',
        'updated_at',
    )
    list_display_links = ('id', 'title')
    list_filter = ('assignment_type', 'status', 'deadline')
    search_fields = ('title', 'description')
    ordering = ('-deadline',)
    date_hierarchy = 'deadline'


class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'student', 'attempts',
                    'extracted_text', 'ai_score', 'created_at', 'updated_at')


admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentSubmission, AssignmentSubmissionAdmin)
admin.site.register(AssignmentSubmissionFile)
