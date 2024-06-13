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
import json 
from django.contrib.auth import get_user_model
import tempfile
import os
import datetime 
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
    return render(request, 'myapp/luyentap.html')
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

    return result
def run_code(code, input_data, language):
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix='.c' if language == 'C' else '.cpp' if language == 'C++' else '.py', mode='w', encoding='utf-8') as temp_file:
        temp_file.write(code)
        temp_file.flush()

    output = ''
    error = ''

    if language == 'Python':
        command = ['python', temp_file.name]
    elif language == 'C':
        executable = temp_file.name.replace('.c', '')
        compile_command = ['gcc', temp_file.name, '-o', executable]
        command = [executable]
    elif language == 'C++':
        executable = temp_file.name.replace('.cpp', '')
        compile_command = ['g++', temp_file.name, '-o', executable]
        command = [executable]
    else:
        return '', f'Unsupported language: {language}'

    try:
        if language in ['C', 'C++']:
            compile_result = subprocess.run(compile_command, capture_output=True)
            if compile_result.returncode != 0:
                error = compile_result.stderr.decode('utf-8')
                return output, error

        result = subprocess.run(
            command,
            input=input_data.encode('utf-8'),
            capture_output=True,
            timeout=5
        )
        try:
            output = result.stdout.decode('utf-8').strip()
        except UnicodeDecodeError:
            output = result.stdout.decode('latin-1').strip()  # Try a fallback encoding
        try:
            error = result.stderr.decode('utf-8').strip()
        except UnicodeDecodeError:
            error = result.stderr.decode('latin-1').strip()  # Try a fallback encoding
    except subprocess.TimeoutExpired:
        output = ''
        error = 'Timeout: Your code took too long to execute.'
    except subprocess.CalledProcessError as e:
        output = ''
        error = f"Error running code: {e}"  # Provide more detailed error information

    os.remove(temp_file.name)
    if language in ['C', 'C++']:
        os.remove(executable)

    return output, error
def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    test_cases = TestCase.objects.filter(problem=problem)

    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            language = form.cleaned_data['language']
            results = []

            for test_case in test_cases:
                output, error = run_code(code, test_case.input_data, language)
                passed = output == test_case.expected_output.strip()
                results.append({
                    'input': test_case.input_data,
                    'expected_output': test_case.expected_output,
                    'output': output,
                    'error': error,
                    'passed': passed,
                })

            # Save the submission
            submission = Submission.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language,
                execution_time=sum(r['execution_time'] for r in results if 'execution_time' in r),
                memory_usage=sum(r['memory_usage'] for r in results if 'memory_usage' in r),
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