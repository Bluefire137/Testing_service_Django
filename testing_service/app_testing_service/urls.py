from django.urls import path
from . import views
from .views import user_login

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', user_login, name='login'),
    path('', views.test_list, name='test_list'),
    path('test/<int:test_id>/', views.take_test, name='take_test'),
    path('test/<int:test_id>/question/<int:question_id>/', views.take_test, name='take_test'),
    path('result/<int:test_id>/', views.test_result, name='test_result'),
]
