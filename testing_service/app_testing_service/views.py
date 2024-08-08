from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .models import Test, Question, Answer, UserTestResult, UserAnswer
from .forms import SignUpForm, TakeTestForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse


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
    questions = list(test.questions.filter(is_active=True).order_by('id'))

    if question_id:
        question = get_object_or_404(Question, id=question_id)
        if question not in questions:
            return redirect('take_test', test_id=test.id, question_id=questions[0].id)
    else:
        question = questions[0]

    current_index = questions.index(question)
    previous_question_id = questions[current_index - 1].id if current_index > 0 else None
    next_question_id = questions[current_index + 1].id if current_index < len(questions) - 1 else None

    if request.method == 'POST':
        form = TakeTestForm(request.POST, question=question)
        if form.is_valid():
            selected_answers = form.cleaned_data['ответы']
            correct_answers = question.answers.filter(is_correct=True)

            is_correct = set(selected_answers) == set(correct_answers)

            user_answer = UserAnswer.objects.create(
                user=request.user,
                question=question,
                is_correct=is_correct,
            )
            user_answer.selected_answers.set(selected_answers)

            if next_question_id:
                return redirect('take_test', test_id=test.id, question_id=next_question_id)
            else:
                total_correct_answers = 0
                total_possible_correct_answers = 0

                for question in questions:
                    correct_answers = question.answers.filter(is_correct=True)
                    total_possible_correct_answers += correct_answers.count()
                    user_answers = UserAnswer.objects.filter(user=request.user, question=question)
                    if user_answers.exists():
                        selected_answers = user_answers.first().selected_answers.all()
                        if set(selected_answers) == set(correct_answers):
                            total_correct_answers += correct_answers.count()

                score = (total_correct_answers / total_possible_correct_answers) * 100
                UserTestResult.objects.create(user=request.user, test=test, score=score)
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
    user_test_results = UserTestResult.objects.filter(user=request.user, test=test).order_by('-created_at')

    if user_test_results.exists():
        test_result = user_test_results.first()
    else:
        return redirect('test_list')

    total_correct_answers = UserAnswer.objects.filter(user=request.user, question__test=test, is_correct=True).count()
    total_possible_correct_answers = sum(q.answers.filter(is_correct=True).count() for q in test.questions.all())

    context = {
        'test': test,
        'score': test_result.score,
        'total_correct_answers': total_correct_answers,
        'total_possible_correct_answers': total_possible_correct_answers,
    }
    return render(request, 'app_testing_service/test_result.html', context)
