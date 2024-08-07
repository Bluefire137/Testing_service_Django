from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Test, Question, Answer

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class TakeTestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question')
        super(TakeTestForm, self).__init__(*args, **kwargs)

        self.fields['ответы'] = forms.ModelMultipleChoiceField(
            queryset=question.answers.all(),
            widget=forms.CheckboxSelectMultiple,
            required=True,
        )
