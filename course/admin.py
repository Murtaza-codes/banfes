from django.contrib import admin

from .models import Program, Course, CourseAllocation, Upload, Topic, UploadVideo
from modeltranslation.admin import TranslationAdmin

class ProgramAdmin(TranslationAdmin):
    pass
class CourseAdmin(TranslationAdmin):
    pass
class UploadAdmin(TranslationAdmin):
    pass

class VideoAdmin(TranslationAdmin):
    pass
class TopicAdmin(TranslationAdmin):
    pass

admin.site.register(Program, ProgramAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(CourseAllocation)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Upload, UploadAdmin)
admin.site.register(UploadVideo, VideoAdmin)