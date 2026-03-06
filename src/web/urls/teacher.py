from django.urls import path
from src.web import views


urlpatterns = [
    # Кабинет Учителя (Tabs)
    path('', views.TeacherDashboardView.as_view(), name='web-teacher-dashboard'),
    path('students/<uuid:student_id>/', views.StudentDetailView.as_view(), name='web-student-detail'),
    path('invitation/add/', views.CreateInvitationView.as_view(), name='web-create-invitation'),
    path('invitation/<uuid:pk>/edit/', views.InvitationUpdateView.as_view(), name='web-invitation-edit'),
    path('invitation/<uuid:pk>/delete/', views.InvitationDeleteView.as_view(), name='web-invitation-delete'),


    # Управление Курсами
    path('courses/create/', views.CourseCreateView.as_view(), name='web-course-create'),
    path('courses/<uuid:pk>/edit/', views.CourseUpdateView.as_view(), name='web-course-edit'),
    path('courses/<uuid:pk>/delete/', views.CourseDeleteView.as_view(), name='web-course-delete'),
    path('courses/<uuid:course_id>/assign/', views.CourseAssignmentView.as_view(), name='web-course-assign'),

    # Управление Юнитами (LearningUnit)
    path('courses/<uuid:course_id>/unit/add/', views.UnitCreateView.as_view(), name='web-unit-create'),
    path('unit/<uuid:pk>/edit/', views.UnitUpdateView.as_view(), name='web-unit-edit'),
    path('unit/<uuid:pk>/delete/', views.UnitDeleteView.as_view(), name='web-unit-delete'),

]