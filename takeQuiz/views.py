from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView

from .decorators import student_required
from .forms import SignUpForm, TakeQuizForm, StudentSubjectsForm
from .models import Quiz, Student, TakenQuiz, User


def home(request):
    if request.user.is_authenticated:
        return redirect('students:quiz_list')
    return render(request, 'takeQuiz/home.html')


class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = 'signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('students:quiz_list')

@method_decorator([login_required, student_required], name='dispatch')
class StudentSubjectsView(UpdateView):
    model = Student
    form_class = StudentSubjectsForm
    template_name = 'takeQuiz/students/subjects_form.html'
    success_url = reverse_lazy('students:quiz_list')

    def get_object(self):
        return self.request.user.student

    def form_valid(self, form):
        return super().form_valid(form)


@method_decorator([login_required, student_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'takeQuiz/students/quiz_list.html'

    def get_queryset(self):
        student = self.request.user.student
        student_subjects = student.subjects.values_list('pk', flat=True)
        taken_quizzes = student.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=student_subjects) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, student_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'takeQuiz/students/taken_quiz.html'

    def get_queryset(self):
        queryset = self.request.user.student.taken_quizzes \
            .select_related('quiz') \
            .order_by('quiz__name')
        return queryset


@login_required
@student_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    student = request.user.student

    if student.quizzes.filter(pk=pk).exists():
        return render(request, 'students/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = student.get_unanswered_questions(quiz)
    unanswered_questions_count= unanswered_questions.count()
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                student_answer = form.save(commit=False)
                student_answer.student = student
                student_answer.save()
                if student.get_unanswered_questions(quiz).exists():
                    return redirect('students:take_quiz', pk)
                else:
                    correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    TakenQuiz.objects.create(student=student, quiz=quiz, correct_answer=correct_answers, total_question=total_questions)
                    return redirect('students:completed_quiz', pk)
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'takeQuiz/students/take_quiz.html', {
        'quiz': quiz,
        'unanswered_questions_count':unanswered_questions_count,
        'question': question,
        'form': form,
    })


@login_required
@student_required
def confirm_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    return render(request, 'takeQuiz/students/confirm_quiz.html',{
        'quiz' : quiz,
    })


@login_required
@student_required
def completed_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk = pk)
    student = request.user.student
    if student.get_unanswered_questions(quiz).exists():
        return redirect('students:quiz_list')
    total_questions = quiz.questions.count()
    correct_answers = student.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
    return render(request, 'takeQuiz/students/completed_quiz.html', {
        'quiz': quiz,
        'total_questions': total_questions,
        'correct_answers' : correct_answers,
    })