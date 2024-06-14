from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User
from .models import Course, CourseProblem, Problem, ProblemTag, Submission, Tag,  TestCase, Leaderboard
from django.http import JsonResponse
from .forms import *
import subprocess
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
import requests
from django.contrib.auth import update_session_auth_hash
import json 
from django.contrib.auth import get_user_model
import tempfile
import os
import datetime 
from .forms import UserUpdateForm, CustomPasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
import django 
from .forms import CodeSubmissionForm
from django.http import JsonResponse
def user_list(request):
    users = User.objects.all()
    return render(request, 'myapp/user_list.html', {'users': users})
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'myapp/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'myapp/login.html', {'form': form})

def home(request):
    courses = Course.objects.all()
    return render(request, 'myapp/home.html', {'courses': courses})
def trangchu(request):
    courses = Course.objects.all()
    return render(request, 'myapp/trangchu.html',{'courses': courses})

def thongtin(request):
    return render(request, 'myapp/thongtin.html')

def allkhoahoc(request):
    return render(request, 'myapp/allkhoahoc.html')

def luyentap(request):
    tags = Tag.objects.all()
    problems = Problem.objects.all().order_by('id')
    return render(request, 'myapp/luyentap.html', {
        'tags': tags,
        'problems': problems,
    })

def setting(request):
    return render(request, 'myapp/setting.html') 


def all_courses(request):
    courses = Course.objects.all()
    return render(request, 'myapp/allkhoahoc.html', {'courses': courses})
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'myapp/course_detail.html', {'course': course})

def all_problems(request):
    tags = Tag.objects.all()
    problems = Problem.objects.all()
    return render(request, 'myapp/luyentap.html',  {'tags': tags, 'problems': problems})

#curd problems
def problem_list(request):
    tags = Tag.objects.all()
    problems = Problem.objects.all()
    return render(request, 'myapp/problem_list.html', {'tags': tags, 'problems': problems})
def problems_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    problems = Problem.objects.filter(tags=tag)
    return render(request, 'myapp/problems_by_tag.html', {'tag': tag, 'problems': problems})
PISTON_API_URL = "https://emkc.org/api/v2/piston/execute"


@csrf_exempt
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    test_cases = TestCase.objects.filter(problem=problem)
    result = None

def run_code_jdoodle(code, language, input_data):
    url = "https://api.jdoodle.com/v1/execute"
    
    if language in ['c', 'cpp']:
        # Tạo tệp tạm thời để lưu trữ dữ liệu đầu vào
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_input:
            temp_input.write(input_data)
            temp_input.flush()
            input_file = temp_input.name
        
        # Đọc dữ liệu đầu vào từ tệp
        with open(input_file, 'r') as file:
            input_data = file.read()
    
    payload = {
        "clientId": "f032a9b764d0c14c77a666efd08df81e",         # Thay YOUR_CLIENT_ID bằng clientId của bạn từ JDoodle
        "clientSecret": "d03d42e5cbc39bd3ab466b0f03d2735011456ff3639245f911d290a07d42b09f", # Thay YOUR_CLIENT_SECRET bằng clientSecret của bạn từ JDoodle
        "script": code,
        "language": language,
        "versionIndex": "0",
        "stdin": input_data
    }
    response = requests.post(url, json=payload)
    return response.json()

def run_code(code, input_data, language):
    if language == 'Python':
        jdoodle_language = 'python3'
    elif language == 'C':
        jdoodle_language = 'c'
    elif language == 'C++':
        jdoodle_language = 'cpp17'
    else:
        return '', f'Unsupported language: {language}'

    result = run_code_jdoodle(code, jdoodle_language, input_data)
    output = result.get('output', '')
    error = result.get('error', '')

    if result.get('statusCode') != 200:
        error = result.get('error', '')

    return output, error, False

def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    test_cases = TestCase.objects.filter(problem=problem)

    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            language = form.cleaned_data['language']
            results = []
            timeout_error_occurred = False

            for test_case in test_cases:
                output, error, timeout_error = run_code(code, test_case.input_data, language)
                if timeout_error:
                    timeout_error_occurred = True
                passed = output.strip() == test_case.expected_output.strip()
                results.append({
                    'input': test_case.input_data,
                    'expected_output': test_case.expected_output,
                    'output': output,
                    'error': error,
                    'passed': passed,
                })

            if timeout_error_occurred:
                return JsonResponse({'error': 'Timeout: Your code took too long to execute.'}, status=400)

            # Save the submission
            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language,
                execution_time=0,  # Không có thông tin thời gian thực thi từ JDoodle
                memory_usage=0,    # Không có thông tin sử dụng bộ nhớ từ JDoodle
                output=output,
                passed=all(r['passed'] for r in results),
                error='\n'.join(r['error'] for r in results if r['error'])
            )

            return JsonResponse({'results': results})

    else:
        form = CodeSubmissionForm()

    # Fetch previous submissions
    previous_submissions = Submission.objects.filter(user=request.user, problem=problem).order_by('-submission_time')

    return render(request, 'myapp/submit_code.html', {
        'form': form,
        'problem': problem,
        'previous_submissions': previous_submissions
    })
def edit_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST, initial={'code': submission.code, 'language': submission.language})
        if form.is_valid():
            submission.code = form.cleaned_data['code']
            submission.language = form.cleaned_data['language']
            submission.save()
            return redirect('submit_code', problem_id=submission.problem.id)
    else:
        form = CodeSubmissionForm(initial={'code': submission.code, 'language': submission.language})

    return render(request, 'myapp/edit_submission.html', {
        'form': form,
        'submission': submission,
        'problem': submission.problem,
    })
@login_required
def thongtin(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        
        if 'update_user' in request.POST:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Tài khoản của bạn đã được cập nhật!')
                return redirect('thongtin')

        if 'change_password' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Mật khẩu của bạn đã được cập nhật!')
                return redirect('thongtin')
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'myapp/thongtin.html', {
        'user_form': user_form,
        'password_form': password_form
    })
    