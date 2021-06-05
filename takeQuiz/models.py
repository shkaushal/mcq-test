from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
from datetime import date, datetime, timedelta


class User(AbstractUser):
    is_student = models.BooleanField(default=False)


class Subject(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        html = '<span class = "badge badge-secondary" style="color: #0f292f">%s</span>' % (name)
        return mark_safe(html)


class Quiz(models.Model):
    name = models.CharField(max_length=255)
    date_created = models.DateField(default=date.today(), blank=True)
    expiration_date = models.DateField(default=date.today() + timedelta(15), blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField('Question', max_length=255)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField('Choice', max_length=255)
    is_correct = models.BooleanField('Correct answer', default=False)

    def __str__(self):
        return self.text


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    quizzes = models.ManyToManyField(Quiz, through='TakenQuiz')
    subjects = models.ManyToManyField(Subject, related_name='interested_students')

    def get_unanswered_questions(self, quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    def __str__(self):
        return self.user.username


class TakenQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_quizzes')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes')
    correct_answer = models.IntegerField()
    total_question = models.IntegerField()
    date = models.DateField(default=date.today(), blank=True)


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_answers')
    answer = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='+')