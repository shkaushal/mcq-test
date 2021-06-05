from django.urls import include, path
from .views import home, QuizListView, TakenQuizListView, StudentSubjectsView, take_quiz, completed_quiz, confirm_quiz

urlpatterns = [
    path('', home, name='home'),
    path('students/', include(([
        path('', QuizListView.as_view(), name = 'quiz_list'),
        path('subjects/', StudentSubjectsView.as_view(), name='student_subjects'),
        path('quiztaken/', TakenQuizListView.as_view(), name = 'taken_quiz'),
        path('quiz/<int:pk>/', take_quiz, name = 'take_quiz'),
        path('confirm_quiz/<int:pk>/', confirm_quiz, name = 'confirm_quiz'),
        path('completed_quiz/<int:pk>/', completed_quiz, name = 'completed_quiz'),
    ], 'takeQuiz'), namespace='students')),
]