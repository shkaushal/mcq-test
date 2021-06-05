from django.contrib import admin
from .models import User, Quiz, Question, Choice, Student, Subject

admin.site.register(User)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Student)
admin.site.register(Subject)
