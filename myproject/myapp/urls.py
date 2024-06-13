from django.urls import path
from . import views
# from .views import evaluate_submission, problem_detail
urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home, name='home'),
    path('users/', views.user_list, name='user_list'), 
    path('trangchu/', views.trangchu, name='trangchu'),
    path('thongtin/', views.thongtin, name='thongtin'),
    path('allkhoahoc/', views.all_courses, name='all_courses'),
    path('luyentap/', views.luyentap, name='luyentap'),
    path('setting/', views.setting, name='setting'),
    path('problems/', views.problem_list, name='problem_list'),
    path('tag/<int:tag_id>/', views.problems_by_tag, name='problems_by_tag'),
    path('problem/<int:problem_id>/', views.problem_detail, name='problem_detail'),
     path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    #  path('problem/<int:problem_id>/submit/', views.submit_code, name='submit_code'),
     path('luyentap/', views.all_problems, name='all_problems'), 
    # path('evaluate/', evaluate_submission, name='evaluate_submission'),
    path('submit_code/<int:problem_id>/', views.submit_code, name='submit_code'),

]