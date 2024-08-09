from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import SignUpForm, TakeTestForm
from .models import Test, Question, UserTestResult, UserAnswer


def home_redirect(request):
    return HttpResponseRedirect(reverse('test_list'))


def test_list(request):
    tests = Test.objects.filter(is_active=True)
    return render(request, 'app_testing_service/test_list.html', {'tests': tests})


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('test_list')
    else:
        form = SignUpForm()
    return render(request, 'app_testing_service/signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('test_list')
    else:
        form = AuthenticationForm()
    return render(request, 'app_testing_service/login.html', {'form': form})


@login_required
def take_test(request, test_id, question_id=None):
    test = get_object_or_404(Test, id=test_id, is_active=True)
    user_test_results = UserTestResult.objects.filter(user=request.user, test=test)
    if user_test_results:
        user_test_results.delete()
        UserAnswer.objects.filter(user=request.user, test=test).delete()

    user_questions_ids = UserAnswer.objects.filter(user=request.user, test=test).values_list('question__id', flat=True)
    all_questions = list(test.questions.filter(is_active=True).order_by('id'))
    access_questions = [question for question in all_questions if question.id not in user_questions_ids]

    if question_id:
        question = get_object_or_404(Question, id=question_id)
        if question not in access_questions:
            return redirect('take_test', test_id=test.id, question_id=access_questions[0].id)
    else:
        question = access_questions[0]

    current_index = access_questions.index(question)
    previous_question_id = access_questions[current_index - 1].id if current_index > 0 else None
    next_question_id = access_questions[current_index + 1].id if current_index < len(access_questions) - 1 else None

    if request.method == 'POST':
        form = TakeTestForm(request.POST, question=question)
        if form.is_valid():
            selected_answers = form.cleaned_data['ответы']
            correct_answers = question.answers.filter(is_correct=True)
            is_correct = set(selected_answers) == set(correct_answers)

            user_answer = UserAnswer.objects.create(
                user=request.user,
                question=question,
                test=test,
                is_correct=is_correct,
            )
            user_answer.selected_answers.set(selected_answers)

            user_answers = UserAnswer.objects.filter(user=request.user, test=test).all()
            remaining_questions = [q for q in all_questions if
                                   q.id not in user_answers.values_list('question__id', flat=True)]

            if next_question_id:
                return redirect('take_test', test_id=test.id, question_id=next_question_id)
            elif remaining_questions:
                return redirect('take_test', test_id=test.id, question_id=remaining_questions[0].id)
            else:
                update_test_result(request.user, test.id)
                return redirect('test_result', test_id=test.id)

    else:
        form = TakeTestForm(question=question)

    context = {
        'form': form,
        'question': question,
        'test': test,
        'previous_question_id': previous_question_id,
        'next_question_id': next_question_id,
    }
    return render(request, 'app_testing_service/take_test.html', context)


@login_required
def test_result(request, test_id):
    test = get_object_or_404(Test, id=test_id, is_active=True)
    user_test_results = UserTestResult.objects.filter(user=request.user, test=test)

    if not user_test_results.exists():
        return redirect('take_test', test_id=test.id)
    test_result = user_test_results.first()
    total_questions = test.questions.all().count()

    context = {
        'test': test,
        'score': test_result.score,
        'total_correct_questions': test_result.total_correct_questions,
        'total_questions': total_questions,
    }
    return render(request, 'app_testing_service/test_result.html', context)


def update_test_result(user, test_id):
    test = get_object_or_404(Test, id=test_id, is_active=True)
    total_correct_questions = 0
    total_questions = test.questions.all().count()

    for question in test.questions.all():
        correct_answers = question.answers.filter(is_correct=True).values_list('id', flat=True)
        user_answer = UserAnswer.objects.filter(user=user, question=question).first()
        selected_answers_ids = user_answer.selected_answers.values_list('id', flat=True)
        if set(selected_answers_ids) == set(correct_answers):
            total_correct_questions += 1

    score = round((total_correct_questions / total_questions) * 100 if total_questions > 0 else 0, 2)

    UserTestResult.objects.create(user=user, test=test, score=score, total_correct_questions=total_correct_questions)
