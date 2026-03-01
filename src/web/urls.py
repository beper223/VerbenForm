from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegisterView.as_view(), name='register'),

    # Student
    path('', views.DashboardView.as_view(), name='units-list'),
    path('training/<int:unit_id>/', views.TrainingSessionView.as_view(), name='training-session'),
    path('training/submit/', views.SubmitAnswerView.as_view(), name='submit-answer'),

    # Teacher
    path('teacher/students/', views.TeacherStudentsView.as_view(), name='teacher-students'),
    path('profile/settings/', views.ProfileSettingsView.as_view(), name='profile-settings'),
]