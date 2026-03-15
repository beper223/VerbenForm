from django.urls import include, path
from src.web import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Auth
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.UserRegisterView.as_view(), name='register'),

    # Profile
    path('profile/', views.ProfileView.as_view(), name='web-profile'),
    path('password-change/', views.MyPasswordChangeView.as_view(), name='password_change'),

    # Student
    path('', views.HomeView.as_view(), name='index'),
    path('dashboard/', views.CourseListView.as_view(), name='units-list'),
    path('course/<uuid:course_id>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('training/<uuid:unit_id>/', views.TrainingSessionView.as_view(), name='training-session'),
    path('training/submit/', views.SubmitAnswerView.as_view(), name='submit-answer'),
    path('unit/<uuid:unit_id>/stats/', views.UnitStatsView.as_view(), name='web-unit-stats-detail'),

    # Teacher
    path('teacher/', include('src.web.urls.teacher')),
    path('api/verbs/search/', views.VerbLookupView.as_view(), name='api-verb-search'),

    path('impressum/', views.ImpressumView.as_view(), name='web-impressum'),
    path('datenschutz/', views.PrivacyView.as_view(), name='web-privacy'),
]