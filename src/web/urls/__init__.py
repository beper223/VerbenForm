from django.urls import include, path
from src.web import views

urlpatterns = [
    # Auth
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('profile/settings/', views.ProfileSettingsView.as_view(), name='profile-settings'),

    # Student
    path('', views.CourseListView.as_view(), name='units-list'),
    path('course/<uuid:course_id>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('training/<uuid:unit_id>/', views.TrainingSessionView.as_view(), name='training-session'),
    path('training/submit/', views.SubmitAnswerView.as_view(), name='submit-answer'),
    path('unit/<uuid:unit_id>/stats/', views.UnitStatsView.as_view(), name='web-unit-stats-detail'),

    # Teacher
    path('teacher/', include('src.web.urls.teacher')),
]