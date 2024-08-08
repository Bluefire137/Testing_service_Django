from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home_redirect),
    path('test_list/', views.test_list, name='test_list'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='test_list'), name='logout'),
    path('test/<int:test_id>/', views.take_test, name='take_test'),
    path('test/<int:test_id>/question/<int:question_id>/', views.take_test, name='take_test'),
    path('result/<int:test_id>/', views.test_result, name='test_result'),
]
