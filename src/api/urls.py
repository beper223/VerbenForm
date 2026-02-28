from django.urls import path, include
from rest_framework.routers import DefaultRouter

from src.api.views import (
    LearningUnitViewSet,
    UserVerbProgressViewSet,
    AuthViewSet,
    TrainingViewSet,
    UserProfileViewSet,
    TeacherViewSet,
    InviteViewSet
)


router = DefaultRouter()
router.register(r'learning-units', LearningUnitViewSet, basename='learning-unit')
router.register(r'verb-progress', UserVerbProgressViewSet, basename='verb-progress')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'training', TrainingViewSet, basename='training')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'invites', InviteViewSet, basename='invites')
router.register(r'teacher', TeacherViewSet, basename='teacher')

urlpatterns = [
    path('', include(router.urls)),
]