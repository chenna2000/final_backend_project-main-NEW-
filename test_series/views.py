import json
from django.shortcuts import get_object_or_404 # type: ignore
from django.http import JsonResponse # type: ignore
from django.utils import timezone # type: ignore
from django.views.decorators.csrf import csrf_exempt # type: ignore
from django.views.decorators.http import require_POST, require_GET # type: ignore
from .models import  ProctoringEvent, ProctoringSession, Exam, Question, UserResponse, UserScore
from .forms import ExamParticipantForm, MarkForReviewForm, StartProctoringSessionForm, EndProctoringSessionForm, RecordProctoringEventForm, SubmitAllAnswersForm, SubmitAnswerForm
from django.core.mail import send_mail # type: ignore
from django.conf import settings # type: ignore
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views import View
from .models import new_user
from django.db.models import Count
import os
from django.utils.text import slugify

def api_response(success, data=None, error=None, details=None, status=200):
    try:
        response = {'success': success}
        if data:
            response['data'] = data
        if error:
            response['error'] = error
        if details:
            response['details'] = details
        return JsonResponse(response, status=status)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class StartProctoringSessionView(View):
    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

            if not token:
                return JsonResponse({'error': 'Token is required'}, status=400)

            user = new_user.objects.filter(token=token).first()
            if not user:
                return JsonResponse({'error': 'Invalid token'}, status=404)

            data = json.loads(request.body.decode('utf-8'))
            form = StartProctoringSessionForm(data)

            if not form.is_valid():
                return JsonResponse({'error': 'Invalid data', 'errors': form.errors}, status=400)

            exam = get_object_or_404(Exam, id=form.cleaned_data['exam_id'])

            if ProctoringSession.objects.filter(user=user, exam=exam).exists():
                return JsonResponse({'error': 'Proctoring session for this exam already exists'}, status=400)

            session = ProctoringSession.objects.create(
                user=user,
                exam=exam,
                start_time=timezone.now(),
                duration=form.cleaned_data.get('duration', timezone.timedelta(hours=3)),
                status='ongoing'
            )

            try:
                send_mail(
                    "Proctoring Session Started",
                    f"Your proctoring session for the exam '{exam.name}' has started.",
                    settings.EMAIL_HOST_USER,
                    [user.email]
                )
            except Exception as email_error:
                return JsonResponse({
                    'success': True,
                    'session_id': session.id,
                    'error': f'Failed to send email to {user.email}',
                    'details': str(email_error)
                }, status=500)

            return JsonResponse({'success': True, 'session_id': session.id}, status=200)

        except (json.JSONDecodeError, IndexError):
            return JsonResponse({'error': 'Invalid JSON or token'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred', 'details': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class EndProctoringSessionView(View):
    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

            if not token:
                return JsonResponse({'error': 'Token is required'}, status=400)

            user = new_user.objects.filter(token=token).first()
            if not user:
                return JsonResponse({'error': 'Invalid token'}, status=404)

            data = json.loads(request.body.decode('utf-8'))
            form = EndProctoringSessionForm(data)

            if not form.is_valid():
                return JsonResponse({'error': 'Invalid data', 'errors': form.errors}, status=400)

            session = get_object_or_404(ProctoringSession, id=form.cleaned_data['session_id'], user=user)

            if session.status == 'completed':
                return JsonResponse({'error': 'Session already completed'}, status=400)

            session.end_time = timezone.now()
            session.status = 'completed'
            session.save()

            try:
                send_mail(
                    "Proctoring Event Notification",
                    "Session ended",
                    settings.EMAIL_HOST_USER,
                    [user.email]
                )
            except Exception as email_error:
                return JsonResponse({
                    'success': True,
                    'data': {'status': 'completed'},
                    'error': f'Failed to send email to {user.email}',
                    'details': str(email_error)
                }, status=500)

            return JsonResponse({'success': True, 'data': {'status': 'completed'}}, status=200)

        except (json.JSONDecodeError, IndexError):
            return JsonResponse({'error': 'Invalid JSON or token'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred while ending the session', 'details': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RecordProctoringEventView(View):
    def post(self, request):
        try:
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

            if not token:
                return JsonResponse({'error': 'Token is required'}, status=400)

            user = new_user.objects.filter(token=token).first()
            if not user:
                return JsonResponse({'error': 'Invalid token'}, status=404)

            data = json.loads(request.body.decode('utf-8'))
            form = RecordProctoringEventForm(data)

            if not form.is_valid():
                return JsonResponse({'error': 'Invalid data', 'errors': form.errors}, status=400)

            session = get_object_or_404(ProctoringSession, id=form.cleaned_data['session_id'], user=user)

            if ProctoringEvent.objects.filter(session=session).exists():
                return JsonResponse({'error': 'Event for this session already recorded'}, status=400)

            event = form.save(commit=False)
            event.session = session
            event.user_id = user.id
            event.save()

            try:
                send_mail(
                    "Proctoring Event Notification",
                    "Event recorded",
                    settings.EMAIL_HOST_USER,
                    [user.email]
                )
            except Exception as email_error:
                return JsonResponse({
                    'success': True,
                    'data': {'status': 'event recorded'},
                    'error': f'Failed to send email to {user.email}',
                    'details': str(email_error)
                }, status=500)

            return JsonResponse({'success': True, 'data': {'status': 'event recorded'}}, status=200)

        except (json.JSONDecodeError, IndexError):
            return JsonResponse({'error': 'Invalid JSON or token'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred while recording the event', 'details': str(e)}, status=500)


@csrf_exempt
@require_POST
def submit_answer(request):
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return api_response({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).first()
        if not user:
            return api_response({'error': 'Invalid token'}, status=403)

        form = SubmitAnswerForm(json.loads(request.body))
        if not form.is_valid():
            return api_response(success=False, error='Invalid data', status=400)

        session_id = form.cleaned_data['session_id']
        question_no = form.cleaned_data['question_no']
        selected_option = form.cleaned_data['selected_option']
        clear_response = form.cleaned_data['clear_response']

        session = get_object_or_404(
            ProctoringSession.objects.select_related('exam').only('id', 'exam_id'), 
            id=session_id, 
            user=user
        )

        question = get_object_or_404(
            Question.objects.only('id', 'status', 'correct_option'), 
            exam_id=session.exam_id, 
            question_no=question_no
        )

        user_response = UserResponse.objects.filter(user=user, question=question, session=session).first()

        if clear_response:
            if user_response:
                if user_response.selected_option == question.correct_option:
                    user_score, _ = UserScore.objects.get_or_create(user=user, exam_id=session.exam_id)
                    if user_score.score > 0:
                        user_score.score -= 1
                        user_score.save(update_fields=['score'])
                user_response.delete()
            return api_response(success=True, data={'message': 'Response cleared and score updated.'})

        if user_response:
            return api_response(success=False, error='Answer already submitted', status=400)

        UserResponse.objects.create(
            user=user,
            question=question,
            session=session,
            selected_option=selected_option,
            response_time=timezone.now()
        )

        if question.status != 'Answered':
            Question.objects.filter(id=question.id).update(status='Answered')

        if selected_option == question.correct_option:
            user_score, _ = UserScore.objects.get_or_create(user=user, exam_id=session.exam_id)
            user_score.score += 1
            user_score.save(update_fields=['score'])

        return api_response(success=True, data={'message': 'Answer submitted successfully'})

    except json.JSONDecodeError:
        return api_response(success=False, error='Invalid JSON format', status=400)
    except Exception as e:
        return api_response(success=False, error='An error occurred while submitting the answer', details=str(e), status=500)


@csrf_exempt
@require_GET
def get_session_status(request, session_id):
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        session = get_object_or_404(ProctoringSession, id=session_id, user=user)
        questions = session.exam.questions.all()

        status_counts = questions.values('status').annotate(count=Count('status'))
        status_dict = {item['status']: item['count'] for item in status_counts}

        remaining_time = session.duration - (timezone.now() - session.start_time)

        status = {
            'answered_questions': status_dict.get("Answered", 0),
            'not_answered_questions': status_dict.get("Not Answered", 0),
            'marked_for_review': status_dict.get("Mark for Review", 0),
            'not_visited_questions': status_dict.get("Not Visited", 0),
            'remaining_time': max(0, remaining_time.total_seconds()),
            'total_questions': questions.count(),
        }

        return api_response(status, status=200)

    except Exception as e:
        return api_response({'error': 'An error occurred while fetching session status', 'details': str(e)}, status=500)


@csrf_exempt
@require_GET
def get_question_details(request, session_id, question_no):
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        session = get_object_or_404(ProctoringSession.objects.select_related('exam'), id=session_id, user=user)
        question = get_object_or_404(Question.objects.only(
            'question_no', 'question_text', 'option1', 'option2', 'option3', 'option4', 'status', 'section'
        ), exam=session.exam, question_no=question_no)

        response_data = {
            'question_no': question.question_no,
            'question_text': question.question_text,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4,
            'status': question.status,
            'section': question.section,
        }

        return api_response(success=True, data=response_data)

    except Exception as e:
        return api_response(
            success=False,
            error='An error occurred while fetching the question details',
            details=str(e),
            status=500
        )

@csrf_exempt
@require_GET
def count_questions(request, exam_id):
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).only('id').first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        exam = Exam.objects.filter(id=exam_id).only('id', 'name').first()
        if not exam:
            return api_response(success=False, error='Exam ID not found', status=404)

        question_count = Question.objects.filter(exam_id=exam_id).count()

        return api_response(success=True, data={'question_count': question_count, 'exam_name': exam.name})

    except Exception as e:
        return api_response(success=False, error='An error occurred while counting questions', details=str(e), status=500)


@csrf_exempt
@require_POST
def mark_for_review(request):
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return api_response(success=False, error='Invalid JSON format', status=400)

        form = MarkForReviewForm(data)
        if not form.is_valid():
            return api_response(success=False, error='Invalid data', details=form.errors, status=400)
        
        session_id = form.cleaned_data['session_id']
        question_no = form.cleaned_data['question_no']
        mark = form.cleaned_data['mark']

        session = get_object_or_404(ProctoringSession.objects.only('id', 'exam'), id=session_id, user=user)
        question = get_object_or_404(Question.objects.only('id', 'status'), exam=session.exam, question_no=question_no)

        new_status = 'Mark for Review' if mark else 'Not Answered'

        if question.status == new_status:
            return api_response(success=True, data={'status': f'Already marked as {new_status.lower()}'})

        question.status = new_status
        question.save(update_fields=['status'])

        message = 'Question marked for review' if mark else 'Mark for review removed'
        return api_response(success=True, data={'status': message})

    except Exception as e:
        return api_response(success=False, error='An error occurred while marking the question for review', details=str(e), status=500)


@require_GET
def fetch_event_types(request):
    try:
        event_types = list(ProctoringEvent.objects.filter(event_type__isnull=False)
                           .exclude(event_type='')
                           .values_list('event_type', flat=True)
                           .distinct())
        return api_response({'event_types': event_types})
    except Exception as e:
        return api_response({'status': 'error', 'message': str(e)}, status=500)

@require_GET
def fetch_section_types(request):
    try:
        section_types = list(Question.objects.filter(section__isnull=False)
                             .exclude(section='')
                             .values_list('section', flat=True)
                             .distinct())
        return api_response({'section_types': section_types})
    except Exception as e:
        return api_response({'status': 'error', 'message': str(e)}, status=500)

@require_GET
def fetch_status_types(request):
    try:
        status_types = list(Question.objects.filter(status__isnull=False)
                             .exclude(status='')
                             .values_list('status', flat=True)
                             .distinct())
        return api_response({'status_types': status_types})
    except Exception as e:
        return api_response({'status': 'error', 'message': str(e)}, status=500)


class StatusTypeChoicesAPIView(APIView):
    def get(self, request, fmt=None):
        try:
            session_type_choices = dict(ProctoringSession.STATUS_CHOICES)
            return api_response({'choices': session_type_choices}, status=200)
        except Exception as e:
            return api_response({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def get_details(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        data = json.loads(request.body)
        session_id = data.get('session_id')
        email = data.get('email', '').strip().lower()

        if not session_id:
            return JsonResponse({'error': 'Session ID is required'}, status=400)

        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        if user.email.lower() != email:
            return JsonResponse({'error': 'Email does not match'}, status=403)

        session = get_object_or_404(ProctoringSession, id=session_id, user=user)
        exam = session.exam

        user_score = UserScore.objects.filter(user=user, exam=exam).only('score').first()
        score = user_score.score if user_score else 0

        question_status_counts = exam.questions.values('status').annotate(count=Count('status'))
        status_mapping = {'Answered': 0, 'Not Answered': 0, 'Not Visited': 0, 'Mark for Review': 0}

        for entry in question_status_counts:
            status_mapping[entry['status']] = entry['count']

        details = {
            'Name': data.get('name', ''),
            'Phone': data.get('mobile_no', ''),
            'Email': user.email,
            'Score': score,
            'answered_questions': status_mapping['Answered'],
            'not_answered_questions': status_mapping['Not Answered'],
            'marked_for_review': status_mapping['Mark for Review'],
            'not_visited_questions': status_mapping['Not Visited'],
        }

        return JsonResponse({'Quiz Summary': details}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred', 'details': str(e)}, status=500)

@csrf_exempt
@require_POST
def submit_all_answers(request):
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        form = SubmitAllAnswersForm(json.loads(request.body))
        if form.is_valid():
            session_id = form.cleaned_data['session_id']
            answers = form.cleaned_data['answers']

            session = get_object_or_404(ProctoringSession, id=session_id, user=user)

            if session.is_submitted:
                return JsonResponse({'error': 'Answers have already been submitted'}, status=400)

            user_score, _ = UserScore.objects.get_or_create(user=user, exam=session.exam)

            question_map = {q.question_no: q for q in session.exam.questions.all()}
            current_time = timezone.now()
            initial_score = user_score.score

            for answer in answers:
                question_no = answer['question_no']
                selected_option = answer['selected_option']
                question = question_map.get(question_no)

                if question:
                    response, created = UserResponse.objects.get_or_create(
                        user=user,
                        question=question,
                        session=session,
                        defaults={'selected_option': selected_option, 'response_time': current_time}
                    )

                    if not created and response.selected_option == question.correct_option and selected_option != question.correct_option:
                        user_score.score = max(user_score.score - 1, 0)

                    if selected_option == question.correct_option and (created or response.selected_option != selected_option):
                        user_score.score += 1

                    response.selected_option = selected_option
                    response.response_time = current_time
                    response.save()

                    question.status = 'Answered'
                    question.save()

            if user_score.score != initial_score:
                user_score.save(update_fields=['score'])

            session.is_submitted = True
            session.save(update_fields=['is_submitted'])

            return JsonResponse({'success': True, 'message': 'Answers submitted successfully'}, status=200)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid data', 'details': form.errors}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred while submitting all answers', 'details': str(e)}, status=500)

@csrf_exempt
@require_GET
def get_next_question(request, session_id, current_question_no):
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).only('id').first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        session = get_object_or_404(ProctoringSession.objects.select_related('exam'), id=session_id, user=user)

        next_question = (
            Question.objects.filter(exam_id=session.exam_id, question_no__gt=current_question_no)
            .order_by('question_no')
            .values('question_no', 'question_text', 'option1', 'option2', 'option3', 'option4', 'status', 'section')
            .first()
        )

        if not next_question:
            return JsonResponse({'success': False, 'error': 'No next question available'}, status=404)

        return JsonResponse(next_question, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred while fetching the next question', 'details': str(e)}, status=500)

@csrf_exempt
@require_GET
def get_previous_question(request, session_id, current_question_no):
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).only('id').first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        session = get_object_or_404(ProctoringSession.objects.select_related('exam'), id=session_id, user=user)

        previous_question = (
            Question.objects.filter(exam_id=session.exam_id, question_no__lt=current_question_no)
            .order_by('-question_no')
            .values('question_no', 'question_text', 'option1', 'option2', 'option3', 'option4', 'status', 'section')
            .first()
        )

        if not previous_question:
            return JsonResponse({'success': False, 'error': 'No previous question available'}, status=404)

        return JsonResponse(previous_question, status=200)

    except Exception as e:
        return JsonResponse({'success': False, 'error': 'An error occurred while fetching the previous question', 'details': str(e)}, status=500)

@csrf_exempt
@require_POST
def submit_details(request):
    try:
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else None

        if not token:
            return JsonResponse({'error': 'Token is required'}, status=400)

        user = new_user.objects.filter(token=token).first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        form = ExamParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save(commit=False)

            if participant.email != user.email:
                return JsonResponse({'status': 'error', 'message': 'Email does not match the authenticated user'}, status=403)

            participant.exam_started = True
            participant.save()

            return api_response({
                'status': 'success',
                'message': 'Exam details submitted successfully',
                'participant_id': participant.id,
                'exam_started': participant.exam_started
            })

        return api_response({'status': 'error', 'errors': form.errors})

    except Exception as e:
        return api_response({'status': 'error', 'message': str(e)}, status=500)

@require_GET
def download_test_file(request, session_id):
    try:
        user = new_user.objects.filter(token=request.headers.get('Authorization', '').split(' ')[1]).first()
        if not user:
            return JsonResponse({'error': 'Invalid token'}, status=403)

        session = get_object_or_404(ProctoringSession, id=session_id, user=user)
        exam = session.exam

        file_name = f"{slugify(exam.name)}_test_paper.pdf"
        file_url = f"{settings.MEDIA_URL}tests/{file_name}"

        file_path = os.path.join(settings.MEDIA_ROOT, 'tests', file_name)
        if not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found', 'path': file_path}, status=404)

        return JsonResponse({'success': True, 'message': 'Test Downloaded successfully', 'file_url': file_url})

    except Exception as e:
        return JsonResponse({'error': 'Download failed', 'details': str(e)}, status=500)

