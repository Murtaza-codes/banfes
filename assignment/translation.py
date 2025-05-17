# assignment/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Assignment


@register(Assignment)
class AssignmentTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    empty_values = None
