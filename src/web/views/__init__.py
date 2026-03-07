from src.web.views.users import (
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    ProfileSettingsView,
)
from src.web.views.learning import (
    CourseListView,
    CourseDetailView,
    TrainingSessionView,
    SubmitAnswerView,
)
from src.web.views.teacher.students import (
    StudentDetailView,
    UnitStatsView,
    StudentCourseDetailView,
)
from src.web.views.teacher.invitations import (
    CreateInvitationView,
    InvitationUpdateView,
    InvitationDeleteView,
)
from src.web.views.teacher.dashboard import (
    TeacherDashboardView,
)
from src.web.views.course import (
    CourseCreateView,
    CourseAssignmentView,
    CourseUpdateView,
    CourseDeleteView,
)
from src.web.views.learning_unit import (
    UnitCreateView,
    UnitUpdateView,
    UnitDeleteView,
)

__all__ = [
    'UserLoginView',
    'UserLogoutView',
    'UserRegisterView',
    'ProfileSettingsView',

    'CourseListView',
    'CourseDetailView',
    'TrainingSessionView',
    'SubmitAnswerView',

    'StudentDetailView',
    'StudentCourseDetailView',
    'UnitStatsView',

    'CreateInvitationView',
    'InvitationUpdateView',
    'InvitationDeleteView',
    'TeacherDashboardView',

    'CourseCreateView',
    'CourseAssignmentView',
    'CourseUpdateView',
    'CourseDeleteView',

    'UnitCreateView',
    'UnitUpdateView',
    'UnitDeleteView',
]