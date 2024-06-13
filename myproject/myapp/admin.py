from django.contrib import admin
from .models import *
# Register your models here.
# admin.site.register(User)
admin.site.register(Problem)
admin.site.register(Submission)
admin.site.register(TestCase)
admin.site.register(Leaderboard)
admin.site.register(Tag)
admin.site.register(ProblemTag)
admin.site.register(Course)
admin.site.register(CourseProblem)