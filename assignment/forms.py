from django import forms
from django.utils import timezone
from .models import Assignment, AssignmentSubmission, AssignmentSubmissionFile


class AssignmentForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
        required=True,
        label='Deadline',
    )

    class Meta:
        model = Assignment
        fields = [
            'assignment_type',
            'title',
            'description',
            'status',
            'evaluation_criteria',
            'deadline',
            'allowed_submissions',
            'additional_file',
        ]

    def clean_deadline(self):
        
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError(
                'The deadline must be a future date and time.')
        return deadline


class AssignmentSubmissionForm(forms.ModelForm):
    submission_text = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': 'Enter your text here...'}),
        required=False,
    )
    files_paths = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = AssignmentSubmission
        fields = ['submission_text', 'files_paths']


    def __init__(self, *args, **kwargs):
        self.assignment = kwargs.pop('assignment', None)
        if not self.assignment:
            raise ValueError(
                "AssignmentSubmissionForm requires an 'assignment' argument.")
        super().__init__(*args, **kwargs)


    def clean(self):
        cleaned_data = super().clean()
        submission_text = cleaned_data.get('submission_text')
        files_paths = cleaned_data.get('files_paths')

        if not submission_text and not files_paths:
            raise forms.ValidationError(
                'You must upload at least one file or enter submission text.')

        return cleaned_data


    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            # Create AssignmentSubmissionFile entries for file paths
            if self.cleaned_data.get('files_paths'):
                file_paths = self.cleaned_data['files_paths'].split(',')
                for path in file_paths:
                    print("path in form", path)
                    if path.strip():
                        AssignmentSubmissionFile.objects.create(
                            submission=instance,
                            file=path.strip()
                        )
        return instance
