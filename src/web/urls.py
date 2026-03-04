from django.urls import path
from src.web import views

urlpatterns = [
    # Auth
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('profile/settings/', views.ProfileSettingsView.as_view(), name='profile-settings'),

    # Student
    path('', views.DashboardView.as_view(), name='units-list'),
    path('stats/', views.StudentStatsView.as_view(), name='web-student-stats'),
    path('training/<int:unit_id>/', views.TrainingSessionView.as_view(), name='training-session'),
    path('training/submit/', views.SubmitAnswerView.as_view(), name='submit-answer'),

    # Teacher
    path('teacher/students/', views.TeacherStudentsView.as_view(), name='web-teacher-students'),
    path('teacher/students/<int:student_id>/', views.StudentDetailView.as_view(), name='web-student-detail'),
]