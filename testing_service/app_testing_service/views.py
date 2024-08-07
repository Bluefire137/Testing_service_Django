from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .models import Test, Question, Answer, UserTestResult, UserAnswer
from .forms import SignUpForm, TakeTestForm
from django.contrib.auth.decorators import login_required


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
def test_list(request):
    tests = Test.objects.filter(is_active=True)
    return render(request, 'app_testing_service/test_list.html', {'tests': tests})


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
        return redirect('test_list')  # Или другое действие, если результатов нет

    total_correct_answers = 0
    total_questions = test.questions.count()

    # Проходим по всем вопросам теста
    for question in test.questions.all():
        # Получаем правильные ответы для текущего вопроса
        correct_answers_ids = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
        user_answer = UserAnswer.objects.filter(user=request.user, question=question).first()

        if user_answer:
            # Получаем ответы пользователя для текущего вопроса
            selected_answers_ids = set(user_answer.selected_answers.values_list('id', flat=True))

            # Проверяем, совпадают ли все выбранные пользователем ответы с правильными
            if selected_answers_ids == correct_answers_ids:
                total_correct_answers += 1  # Увеличиваем счетчик за правильный вопрос

    # Вычисляем итоговый балл
    score = (total_correct_answers / total_questions) * 100 if total_questions > 0 else 0

    context = {
        'test': test,
        'score': score,
        'total_correct_answers': total_correct_answers,
        'total_questions': total_questions,
    }
    return render(request, 'app_testing_service/test_result.html', context)
