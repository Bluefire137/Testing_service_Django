from django.contrib import admin
from .models import Test, Question, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    fields = ('text', 'is_correct')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'is_active')
    inlines = [AnswerInline]


class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('text', 'test', 'is_active')
    list_filter = ('test', 'is_active')
    search_fields = ('text',)


class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    inlines = [QuestionInline]


admin.site.register(Test, TestAdmin)
admin.site.register(Question, QuestionAdmin)
