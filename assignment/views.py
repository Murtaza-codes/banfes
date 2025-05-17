# views.py assignment
import os
import json
import google.generativeai as genai
from re import sub
import cohere
import json
from google.cloud import vision
from google.oauth2 import service_account
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .models import (
    Assignment,
    AssignmentSubmission,
    AssignmentSubmissionFile,
)
from .forms import AssignmentForm, AssignmentSubmissionForm
from course.models import Course, Topic
from google.cloud import vision
from google.oauth2 import service_account
from django.utils import timezone
import mammoth
from django.db import transaction
from django.http import Http404

from django.contrib.auth.decorators import login_required
from accounts.decorators import lecturer_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import uuid
from django.conf import settings
from google.generativeai import GenerativeModel
import pathlib


@login_required
@lecturer_required
def assignment_create_view(request, slug):
    course = get_object_or_404(Course, slug=slug)
    topic_id = request.GET.get('topic')
    topic = get_object_or_404(Topic, id=topic_id, course=course) if topic_id else None

    # return error if topic is not found
    if not topic:
        raise Http404("Topic not found")

    if request.method == 'POST':
        # Handle evaluation_criteria file
        eval_file_path = request.POST.get(
            'evaluation_criteria_path', '').strip()
        if eval_file_path:
            eval_file_name = os.path.basename(eval_file_path)
            evaluation_criteria = 'assignment/evaluation_files/' + eval_file_name
        else:
            evaluation_criteria = None

        # Handle additional_file
        additional_file_path = request.POST.get(
            'additional_file_path', '').strip()
        if additional_file_path:
            additional_file_name = os.path.basename(additional_file_path)
            additional_file = 'assignment/additional_files/' + additional_file_name
        else:
            additional_file = None

        # add the evaluation_criteria and additional_file to the form
        form = AssignmentForm(request.POST, initial={
                              'evaluation_criteria': evaluation_criteria, 'additional_file': additional_file})
        
        
        # Validate the form after processing files
        if form.is_valid():
            try:
                assignment = form.save(commit=False)
                assignment.course = course
                assignment.topic = topic
                assignment.evaluation_criteria = evaluation_criteria
                assignment.additional_file = additional_file
                assignment.save()
                messages.success(request, 'Assignment created successfully.')
                return redirect(reverse('assignment_list', kwargs={'slug': slug}))
            except Exception as e:
                # Log the exception as needed
                form.add_error(
                    None, 'An error occurred while saving the assignment.')
                messages.error(request, 'Please correct the errors below.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AssignmentForm()

    return render(request, 'assignment/assignment_form.html', {'form': form, 'course': course})


@login_required
@lecturer_required
def assignment_update_view(request, slug, pk):
    course = get_object_or_404(Course, slug=slug)
    assignment = get_object_or_404(Assignment, pk=pk, course=course)
    if request.method == 'POST':
        # Handle evaluation_criteria file
        eval_file_path = request.POST.get('evaluation_criteria_path', '')
        if eval_file_path:
            # Delete old file
            if assignment.evaluation_criteria:
                assignment.evaluation_criteria.delete(save=False)
            eval_file_name = os.path.basename(eval_file_path)
            assignment.evaluation_criteria.name = 'assignment/evaluation_files/' + eval_file_name

        # Handle additional_file
        additional_file_path = request.POST.get('additional_file_path', '')
        if additional_file_path:
            # Delete old file
            if assignment.additional_file:
                assignment.additional_file.delete(save=False)
            additional_file_name = os.path.basename(additional_file_path)
            assignment.additional_file.name = 'assignment/additional_files/' + additional_file_name

        # add the evaluation_criteria and additional_file to the form
        form = AssignmentForm(request.POST, instance=assignment, initial={
                              'evaluation_criteria': assignment.evaluation_criteria, 'additional_file': assignment.additional_file})
        
        # Validate the form after processing files
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.save()
            messages.success(request, 'Assignment updated successfully.')
            return redirect(reverse('assignment_list', kwargs={'slug': slug}))
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AssignmentForm(instance=assignment)

    return render(request, 'assignment/assignment_form.html', {'form': form, 'course': course, 'object': assignment})


@login_required
@require_POST
def ajax_upload_file(request):
    print("ajax_upload_file called")
    if 'file' not in request.FILES or 'field_name' not in request.POST:
        return JsonResponse({'error': 'Missing parameters'}, status=400)

    upload = request.FILES['file']
    field_name = request.POST['field_name']
    assignment_type = request.POST.get('assignment_type')
    # Validate file size (max 15MB)
    if upload.size > 15 * 1024 * 1024:
        return JsonResponse({'error': 'File size exceeds 15MB limit'}, status=400)

    # Determine the upload directory based on field_name
    if field_name == 'evaluation_criteria_path':
        directory = 'evaluation_files'
        upload_dir = os.path.join(
            settings.MEDIA_ROOT, 'assignment', 'evaluation_files')
    elif field_name == 'additional_file_path':
        directory = 'additional_files'
        upload_dir = os.path.join(
            settings.MEDIA_ROOT, 'assignment', 'additional_files')
    elif field_name == 'submission_files':
        directory = 'submissions'
        # check file size (max 15MB) and file type (image, doc, txt) for assignment type not 'project'
        file_extension = os.path.splitext(upload.name)[1].lower()
        if assignment_type != 'project' and file_extension not in ['.png', '.jpg', '.jpeg', '.webp', '.heic', '.doc', '.docx', '.txt']:
            return JsonResponse({'error': 'Invalid file type'}, status=400)
        elif assignment_type == 'project' and file_extension not in ['.png', '.jpg', '.jpeg', '.webp', '.heic', '.doc', '.docx', '.txt', '.ppt', '.pptx', '.xls', '.xlsx', '.mp3', '.wav', '.flac', '.pdf', '.mp4', '.avi', '.mkv', '.wmv', '.3gp', '.f4v', '.psd', '.ai', '.xd']:
            return JsonResponse({'error': 'Invalid file type'}, status=400)
        upload_dir = os.path.join(
            settings.MEDIA_ROOT, 'assignment', 'submissions', 'files')
    else:
        return JsonResponse({'error': 'Invalid field name'}, status=400)

    os.makedirs(upload_dir, exist_ok=True)

    # Generate a unique filename
    unique_filename = f"{uuid.uuid4().hex}_{upload.name}"
    file_path = os.path.join(upload_dir, unique_filename)
    relative_file_path = os.path.relpath(file_path, settings.MEDIA_ROOT)

    # Save the file
    with open(file_path, 'wb+') as destination:
        for chunk in upload.chunks():
            destination.write(chunk)

    # Generate file URL
    file_url = f"{settings.MEDIA_URL}assignment/{directory}/{os.path.basename(upload_dir)}/{unique_filename}"

    return JsonResponse({
        'file_path': relative_file_path,
        'file_url': file_url,
        'file_name': upload.name,
        'field_name': field_name,
    })


@login_required
@require_POST
def ajax_delete_file(request):
    assignment = None
    if 'assignment_id' in request.POST:
        assignment = get_object_or_404(
            Assignment, pk=request.POST.get('assignment_id'))

    file_path = request.POST.get('file_path')

    if not file_path:
        return JsonResponse({'error': 'No file path provided'}, status=400)
    file_path = os.path.normpath(file_path)
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
    print("full path", full_path)
    print("file path", file_path)
    # Ensure the file is within the assignments directory
    assignments_root = os.path.join(settings.MEDIA_ROOT, 'assignment')
    print("assignments_root", assignments_root)
    if not os.path.abspath(full_path).startswith(os.path.abspath(assignments_root)):
        return JsonResponse({'error': 'Invalid file path'}, status=400)

    # Delete the file
    if os.path.exists(full_path):
        os.remove(full_path)
        # Delete the file from the database if it exists
        if assignment:
            try:
                assignment_additional_file = assignment.additional_file
                assignment.additional_file = None
                assignment_additional_file.delete()
            except Exception as e:
                print("Error deleting file from database: ", e)
        elif 'submission_files' in file_path:
            submission_file = AssignmentSubmissionFile.objects.filter(
                file=file_path).first()
            if submission_file:
                submission_file.delete()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'File not found'}, status=404)


@login_required
def assignment_submission(request, slug, assignment_id):

    course = get_object_or_404(Course, slug=slug)
    assignment = get_object_or_404(
        Assignment, id=assignment_id, course=course)

    # Get existing submission or None
    submission = AssignmentSubmission.objects.filter(
        assignment=assignment,
        student=request.user
    ).first()

    # Clear session data if it doesn't correspond to the current assignment
    submission_id = request.session.get('submission_id')
    if submission_id:
        # Get the submission from the session
        session_submission = AssignmentSubmission.objects.filter(
            id=submission_id).first()
        if session_submission:
            # If the submission's assignment doesn't match the current assignment, clear session data
            if session_submission.assignment.id != assignment.id:
                request.session.pop('submission_id', None)
                request.session.pop('extracted_text', None)
                request.session.pop('submission_text', None)
        else:
            # If no submission found, clear session data
            request.session.pop('submission_id', None)
            request.session.pop('extracted_text', None)
            request.session.pop('submission_text', None)

    # Check deadline
    if assignment.deadline and timezone.now() > assignment.deadline:
        messages.error(
            request, 'The deadline for this assignment has passed.')
        return redirect('assignment_list', slug=course.slug)

    # Calculate remaining submissions
    attempts_left = assignment.allowed_submissions - \
        (submission.attempts if submission else 0)
    if attempts_left < 1 and assignment.assignment_type != 'project':
        # Clear submission-related session data
        request.session.pop('submission_id', None)
        request.session.pop('extracted_text', None)
        request.session.pop('submission_text', None)
        messages.error(
            request, 'You have reached the maximum number of submissions allowed.')
        return redirect('assignment_list', slug=course.slug)

    if request.method == 'POST':
        step = request.POST.get('step')
        if step == 'upload':
            form = AssignmentSubmissionForm(
                request.POST, assignment=assignment)

            if form.is_valid():
                with transaction.atomic():
                    # Delete previous submission if exists
                    if submission:
                        # Delete associated files
                        for sub_file in submission.submission_files.all():
                            if sub_file.file:
                                # Delete physical file
                                if os.path.exists(sub_file.file.path):
                                    os.remove(sub_file.file.path)
                            sub_file.delete()

                        # Reset submission data
                        submission.extracted_text = None
                        submission.submission_text = None
                        submission.ai_score = None
                        submission.teacher_score = None
                        submission.final_score = None
                        submission.ai_feedback = None
                        submission.teacher_feedback = None
                        submission.save()
                    else:
                        # Create new submission
                        submission = AssignmentSubmission.objects.create(
                            assignment=assignment,
                            student=request.user,
                            attempts=submission.attempts if submission else 0
                        )

                    # Get submitted file paths from hidden input
                    files_paths = request.POST.get(
                        'files_paths', '').split(',')
                    # Remove empty strings
                    files_paths = [p for p in files_paths if p]

                    # Create AssignmentSubmissionFile objects
                    for file_path in files_paths:
                        AssignmentSubmissionFile.objects.create(
                            submission=submission,
                            file=file_path
                        )
                    
                    # if type is project then save the submission text and redirect to result page
                    if assignment.assignment_type == 'project':
                        submission.submission_text = form.cleaned_data.get(
                            'submission_text', '')
                        submission.save()
                        messages.success(
                            request, 'Assignment submitted successfully!')
                        return redirect('assignment_result', slug=course.slug, assignment_id=assignment.id)


                    extracted_text = ''
                    if assignment.assignment_type == 'essay':
                        # Extract text from images in order
                        for file_obj in submission.submission_files.all():
                            file_ext = os.path.splitext(
                                file_obj.file.name)[1].lower()
                            if file_ext in ['.png', '.jpg', '.jpeg', '.webp', '.heic']:
                                extracted_text += extract_text_from_image(
                                    file_obj.file) + '\n'
                            elif file_ext in ['.doc', '.docx']:
                                extracted_text += extract_text_from_doc(
                                    file_obj.file) + '\n'
                            elif file_ext == '.txt':
                                with open(file_obj.file.path, 'r', encoding='utf-8') as f:
                                    extracted_text += f.read() + '\n'

                    # Store texts in session for review
                    request.session['submission_id'] = submission.id
                    request.session['extracted_text'] = extracted_text
                    request.session['submission_text'] = form.cleaned_data.get(
                        'submission_text', '')

                    return redirect('assignment_submission', slug=course.slug, assignment_id=assignment.id)
            else:
                messages.error(
                    request, 'Please correct the errors below.')

        elif step == 'review':
            submission_id = request.session.get('submission_id')
            if submission_id:
                submission = get_object_or_404(
                    AssignmentSubmission, id=submission_id)

                # Get reviewed texts
                extracted_text = request.POST.get('extracted_text', '')
                submission_text = request.POST.get(
                    'submission_text', '')

                # Save texts
                submission.extracted_text = extracted_text
                submission.submission_text = submission_text

                # Handle assignment type specific processing
                if assignment.assignment_type == 'problem':
                    # For problems, send images directly to LLM
                    image_files = []
                    for sub_file in submission.submission_files.all():
                        if os.path.splitext(sub_file.file.name)[1].lower() in ['.png', '.jpg', '.jpeg', '.webp', '.heic']:
                            image_files.append(sub_file.file.path)

                    ai_score, ai_feedback = evaluate_problem_submission(
                        image_files, assignment.evaluation_criteria)

                elif assignment.assignment_type == 'essay':
                    # For essays, combine texts and evaluate
                    ai_score, ai_feedback = evaluate_essay_submission(
                        extracted_text, assignment.evaluation_criteria)

                else:  # project type
                    ai_score = None
                    ai_feedback = None

                # Save results
                submission.ai_score = ai_score
                submission.ai_feedback = ai_feedback
                submission.attempts += 1
                submission.save()

                # Clear session
                request.session.pop('submission_id', None)
                request.session.pop('extracted_text', None)
                request.session.pop('submission_text', None)

                messages.success(
                    request, 'Assignment submitted successfully!')
                return redirect('assignment_result', slug=course.slug, assignment_id=assignment.id)
            else:
                request.session.pop('submission_id', None)
                request.session.pop('extracted_text', None)
                request.session.pop('submission_text', None)
                messages.error(
                    request, 'Session expired. Please submit again.')
                return redirect('assignment_submission', slug=course.slug, assignment_id=assignment.id)

    else:
        form = AssignmentSubmissionForm(assignment=assignment)
        step = 'review' if request.session.get(
            'submission_id') else 'upload'

    context = {
        'form': form,
        'assignment': assignment,
        'course': course,
        'step': step,
        'extracted_text': request.session.get('extracted_text', ''),
        'submission_text': request.session.get('submission_text', ''),
        'submission': submission,
        'attempts_left': attempts_left
    }

    return render(request, 'assignment/assignment_submission.html', context)


def evaluate_problem_submission(image_files, evaluation_criteria):
    """Evaluate problem submission by passing images directly to Gemini"""
   

    if not os.environ.get('GEMINI_API_KEY'):
        return None, 'AI scoring not available.'

    try:
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        model = GenerativeModel('gemini-1.5-flash')

        # Images are already provided as paths, just load them
        images = []
        for img_path in image_files:
            if os.path.exists(img_path):
                with open(img_path, "rb") as f:
                    mime_type = f"image/{pathlib.Path(img_path).suffix[1:]}"
                    images.append({
                        "mime_type": mime_type,
                        "data": f.read()
                    })

        if not images:
            return None, 'No valid images found.'


        # prompt = f"""
        # Evaluate these problem solutions based on the criteria:


        # Evaluation Criteria:
        # {evaluation_criteria}

        # The solutions are provided in {len(images)} images.
        # Please analyze each image and provide:
        # 1. Score (0-100)
        # 2. Detailed feedback for each solution
        # 3. Overall assessment

        # Format the response as JSON:
        # {{"score": <overall_score>, "feedback": "<detailed_feedback>"}}

 # Updated prompt with new structure
        prompt = f"""
        *Role*: You are an expert STEM evaluator with multispectral analysis capabilities.
        Analyze the solution in {len(images)} image(s) according to these guidelines:


        *Core Evaluation Framework*:
        1️⃣ *Domain-Specific Rubric* (Dynamically Adapted):
        {evaluation_criteria}

        2️⃣ *Multimodal Analysis*:
        ├─ *Mathematical Content*:
        │  ├─ Symbolic logic validation
        │  ├─ Dimensional analysis
        │  └─ Boundary condition verification
        ├─ *Chemical/Biological Diagrams*:
        │  ├─ Structural accuracy (bond angles, functional groups)
        │  ├─ Reaction mechanism validation
        │  └─ Biological process sequencing
        ├─ *Physics Systems*:
        │  ├─ Free-body diagram analysis
        │  ├─ Unit conversion checks
        │  └─ Energy conservation verification
        └─ *Cross-Domain*:
           ├─ Graph interpretation (slope, intercepts)
           ├─ Experimental setup validation
           └─ Data visualization best practices

        *Error Taxonomy*:
        🟥 Conceptual: Fundamental misunderstanding
        🟧 Procedural: Incorrect methodology
        🟨 Calculation: Arithmetic/algebraic errors
        🟩 Notation: Symbolic/formula formatting
        🟦 Omission: Missing critical steps

        *Response Protocol*:
        1. Perform image segmentation to isolate:
           - Formulas (LaTeX annotation)
           - Diagrams (Vectorization attempt)
           - Text (OCR with context awareness)
        2. Generate step-by-step solution map
        3. Cross-verify with domain knowledge bases
        4. Apply fuzzy matching for alternative solutions
        5. Confidence scoring (0-100%) for each evaluation component

        *Output Schema*:
        ```json
        {{
          "meta": {{
            "domain": "<auto-detected>",
            "complexity": "<low|medium|high>",
            "solution_type": "<analytical|graphical|experimental>"
          }},
          "evaluation": {{
            "score": {{
              "raw": <float>,
              "weighted": <float>,
              "breakdown": {{
                "criteria_1": {{"score": <float>, "weight": <float>}},
                "criteria_2": {{...}}
              }}
            }},
            "feedback": {{
              "strengths": ["list", "of", "valid", "elements"],
              "errors": [
                {{
                  "type": "<error_category>",
                  "coordinates": "(x1,y1,x2,y2)",
                  "step": "<solution_phase>",
                  "description": "<technical_analysis>",
                  "remediation": "<expert_guidance>"
                }}
              ],
              "visual_annotations": {{
                "heatmap": "<base64_encoded>",
                "markers": ["❗", "✅", "⚠️"] 
              }}
            }},
            "confidence": {{
              "overall": <float>,
              "components": {{
                "formulas": <float>,
                "diagrams": <float>,
                "text": <float>
              }}
            }}
          }},
          "alternative_methods": [
            {{
              "approach": "<method_name>",
              "efficiency": "<comparative_rating>",
              "validation": "<cross-check_status>"
            }}
          ]
        }}
        ```
        """
        response = model.generate_content([prompt] + images)
        result = response.text.strip()

        # Extract JSON from response
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        json_str = result[json_start:json_end]

        data = json.loads(json_str)
        return data.get('score'), data.get('feedback')

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None, f'Error during AI evaluation: {str(e)}'


def evaluate_essay_submission(text, evaluation_criteria):
    """Evaluate essay submission using extracted text"""
    if not os.environ.get('COHERE_API_KEY'):
        return None, 'AI scoring not available.'
    print("cohere called for essay")
    co = cohere.Client(os.environ.get('COHERE_API_KEY'))

    prompt = f"""Evaluate this essay based on the criteria:

Evaluation Criteria:
{evaluation_criteria}

Essay Text:
{text}

Provide a score and detailed feedback in JSON format:
{{"score": <score>, "feedback": "<detailed_feedback>"}}
"""

    try:
        response = co.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=500,
            temperature=0.5,
            k=0,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        result = response.generations[0].text.strip()
        data = json.loads(result)
        return data.get('score'), data.get('feedback')
    except Exception as e:
        print(f"Error calling Cohere API: {e}")
        return None, f'Error during AI evaluation: {str(e)}'


def extract_text_from_image(image_file):
    """Extract text from an image using Google Cloud Vision API"""
    credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not credentials_json:
        print('Google Application Credentials JSON not found.')
        return ''

    credentials_info = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info)
    client = vision.ImageAnnotatorClient(credentials=credentials)
    content = image_file.read()
    image_file.seek(0)  # Reset file pointer after reading

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    if response.error.message:
        print(f"Error during text extraction: {response.error.message}")
        return ''

    return response.full_text_annotation.text

# Extract text from a doc/docx file


def extract_text_from_doc(file_input):
    if isinstance(file_input, str):
        # It's a file path
        with open(file_input, 'rb') as doc_file:
            result = mammoth.extract_raw_text(doc_file)
    else:
        # It's a file-like object
        file_input.seek(0)
        result = mammoth.extract_raw_text(file_input)
    return result.value


@login_required
@require_POST
def assignment_back(request, slug, assignment_id):
    # Get the submission
    assignment_submission = AssignmentSubmission.objects.filter(
        student=request.user, assignment_id=assignment_id).first()
    
    if assignment_submission:
        # Get files before deleting submission
        files = AssignmentSubmissionFile.objects.filter(submission=assignment_submission)
        
        # Delete physical files
        for file in files:
            if file.file:
                if os.path.exists(file.file.path):
                    os.remove(file.file.path)
        
        # Delete submission (this will cascade delete AssignmentSubmissionFile records)
        assignment_submission.delete()

    # Clear only extracted text from session
    request.session.pop('submission_id', None)
    request.session.pop('extracted_text', None)
    request.session.pop('submission_text', None)
    # update step to upload for assignment and return response

    return redirect('assignment_submission', slug=slug, assignment_id=assignment_id)


# Assignment Result View
@login_required
def assignment_result(request, slug, assignment_id):
    course = get_object_or_404(Course, slug=slug)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    submission = AssignmentSubmission.objects.filter(
        assignment=assignment, student=request.user).order_by('-created_at').first()

    if not submission:
        messages.error(request, 'You have not submitted this assignment yet.')
        return redirect('assignment_submission', slug=course.slug, assignment_id=assignment.id)

    submission_files = submission.submission_files.all()
    context = {
        'course': course,
        'assignment': assignment,
        'files': submission_files,
        'submission': submission,
    }
    return render(request, 'assignment/assignment_result.html', context)

# Assignment List View


@login_required
def assignment_list(request, slug):
    course = get_object_or_404(Course, slug=slug)
    assignments = Assignment.objects.filter(course=course)

    # Initialize a dictionary to store submission details per assignment
    submission_dict = {}

    if request.user.is_student:
        # Fetch all submissions by the current student for the assignments in this course
        submissions = AssignmentSubmission.objects.filter(
            student=request.user,
            assignment__in=assignments
            # Optimizes DB queries by fetching related assignments
        ).select_related('assignment')

        # Populate the submission_dict with assignment_id as key and submission details as value
        submission_dict = {
            submission.assignment_id: {
                'attempts': submission.attempts,
                'ai_score': submission.ai_score,
                'teacher_score': submission.teacher_score,
                'final_score': submission.final_score,
            }
            for submission in submissions
        }

        # Calculate remaining attempts for each assignment and attach submission details
        for assignment in assignments:
            submission = submission_dict.get(assignment.id)
            if submission:
                attempts = submission['attempts']
                remaining_attempts = assignment.allowed_submissions - attempts
                remaining_attempts = max(remaining_attempts, 0)
                # Attach remaining_attempts and submission details to the assignment instance
                assignment.remaining_attempts = remaining_attempts
                assignment.ai_score = submission['ai_score']
                assignment.teacher_score = submission['teacher_score']
                assignment.final_score = submission['final_score']
            else:
                # No submissions yet; all attempts are remaining
                assignment.remaining_attempts = assignment.allowed_submissions
                assignment.ai_score = None
                assignment.teacher_score = None
                assignment.final_score = None
    else:
        # For non-student users (e.g., lecturers), you can set remaining_attempts and scores as needed
        for assignment in assignments:
            assignment.remaining_attempts = None  # Or any other logic as needed
            assignment.ai_score = None
            assignment.teacher_score = None
            assignment.final_score = None

    context = {
        'assignments': assignments,
        'course': course,
        'submission_dict': submission_dict,
        'today': timezone.localdate(),
        'active_page': 'assignments',
        'now': timezone.now(),
    }
    return render(request, 'assignment/assignment_list.html', context)

# Assignment Submissions View (For Teachers)


@login_required
@lecturer_required
def assignment_submissions(request, slug, assignment_id):
    course = get_object_or_404(Course, slug=slug)
    assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment)
    context = {
        'course': course,
        'assignment': assignment,
        'submissions': submissions,
    }
    return render(request, 'assignment/assignment_submissions.html', context)

# Assignment Submission Detail View (For Teachers)

# views.py


@login_required
@lecturer_required
def assignment_submission_detail(request, slug, assignment_id, submission_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    course = get_object_or_404(Course, slug=slug)

    if request.method == 'POST':
        teacher_score = request.POST.get('teacher_score')
        teacher_feedback = request.POST.get('teacher_feedback')
        if teacher_score:
            try:
                submission.teacher_score = float(teacher_score)
            except ValueError:
                messages.error(
                    request, 'Please enter a valid numeric value for the score.')
                return redirect('assignment_submission_detail', slug=slug, assignment_id=assignment_id, submission_id=submission_id)
            submission.teacher_feedback = teacher_feedback
            # Calculate final score
            if submission.ai_score is not None:
                if submission.teacher_score - submission.ai_score >= 10 or submission.ai_score - submission.teacher_score >= 10:
                    submission.final_score = submission.teacher_score
                else:
                    submission.final_score = (submission.ai_score + submission.teacher_score) / 2
            else:
                submission.final_score = submission.teacher_score
            submission.save()
            messages.success(request, 'Score and feedback saved.')
            return redirect('assignment_submission_detail', slug=slug, assignment_id=assignment_id, submission_id=submission_id)
        else:
            messages.error(request, 'Please enter a score.')
            return redirect('assignment_submission_detail', slug=slug, assignment_id=assignment_id, submission_id=submission_id)

    # Hide AI score until teacher has provided their score
    show_ai_score = submission.teacher_score is not None

    # Get submission files
    submission_files = submission.submission_files.all()

    return render(request, 'assignment/assignment_submission_detail.html', {
        'submission': submission,
        'assignment': assignment,
        'course': course,
        'files': submission_files,
        'show_ai_score': show_ai_score,
    })


@login_required
@lecturer_required
def assignment_delete(request, slug, pk):
    course = get_object_or_404(Course, slug=slug)
    assignment = get_object_or_404(Assignment, pk=pk, course=course)

    try:
        with transaction.atomic():
            # Delete all submission files
            for submission in assignment.submissions.all():
                for submission_file in submission.submission_files.all():
                    try:
                        # Delete physical file if it exists
                        if submission_file.file and os.path.exists(submission_file.file.path):
                            os.remove(submission_file.file.path)
                    except OSError as e:
                        print(f"Error deleting file {submission_file.file}: {e}")
                    submission_file.delete()
                submission.delete()

            # Delete assignment files
            try:
                if assignment.evaluation_criteria and os.path.exists(assignment.evaluation_criteria.path):
                    os.remove(assignment.evaluation_criteria.path)
                if assignment.additional_file and os.path.exists(assignment.additional_file.path):
                    os.remove(assignment.additional_file.path)
            except OSError as e:
                # Log error but continue with deletion
                print(f"Error deleting assignment files: {e}")

            # Delete the assignment
            assignment.delete()
            messages.success(request, 'Assignment deleted successfully.')

    except Exception as e:
        messages.error(request, f'Error deleting assignment: {str(e)}')
        print(f"Error in assignment deletion: {e}")

    return redirect('assignment_list', slug=slug)
