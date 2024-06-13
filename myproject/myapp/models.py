from django.db import models
from django.contrib.auth.models import User


# class User(models.Model):
#     username = models.CharField(max_length=150, unique=True)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=128)

#     def __str__(self):
#         return self.username

class Problem(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=50)
    tags = models.ManyToManyField('Tag', through='ProblemTag')

    def __str__(self):
        return self.title

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=50)
    submission_time = models.DateTimeField(auto_now_add=True)
    execution_time = models.FloatField(default=0)
    memory_usage = models.FloatField(default=0)
    output = models.TextField()
    passed = models.BooleanField(default=False)
    error = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Submission by {self.user.username} for {self.problem.title}'

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return f'TestCase for {self.problem.title}'

class Leaderboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    score = models.IntegerField()
    rank = models.IntegerField()

    def __str__(self):
        return f'{self.user.username} - {self.problem.title}'

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ProblemTag(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.problem.title} - {self.tag.name}'

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title

class CourseProblem(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.course.title} - {self.problem.title}'