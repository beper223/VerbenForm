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
    path('teacher/students/<uuid:student_id>/', views.StudentDetailView.as_view(), name='web-student-detail'),
    path('teacher/invite/', views.CreateInvitationView.as_view(), name='web-create-invitation'),

    # Главный Кабинет Учителя (Tabs)
    path('teacher/dashboard/', views.TeacherDashboardView.as_view(), name='web-teacher-dashboard'),

    # Управление Курсами
    path('teacher/courses/create/', views.CourseCreateView.as_view(), name='web-course-create'),
    path('teacher/courses/<uuid:pk>/edit/', views.CourseUpdateView.as_view(), name='web-course-edit'),
    path('teacher/courses/<uuid:pk>/delete/', views.CourseDeleteView.as_view(), name='web-course-delete'),
    path('teacher/courses/<uuid:course_id>/assign/', views.CourseAssignmentView.as_view(), name='web-course-assign'),

    # Управление Юнитами (LearningUnit)
    path('teacher/courses/<uuid:course_id>/unit/add/', views.UnitCreateView.as_view(), name='web-unit-create'),
    path('teacher/unit/<uuid:pk>/edit/', views.UnitUpdateView.as_view(), name='web-unit-edit'),
    path('teacher/unit/<uuid:pk>/delete/', views.UnitDeleteView.as_view(), name='web-unit-delete'),

    # HTMX переключатели для вкладок (опционально для скорости)
    path('teacher/dashboard/tab/<str:tab_name>/', views.TeacherDashboardTabView.as_view(), name='web-teacher-tab'),
]