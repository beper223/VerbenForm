from src.web.views.users import (
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    ProfileSettingsView,
)
from src.web.views.learning import (
    DashboardView,
    TrainingSessionView,
    SubmitAnswerView,
)
from src.web.views.teacher.students import (
    TeacherStudentsView,
    StudentDetailView,
    StudentStatsView,
)
from src.web.views.teacher.invitations import (
    CreateInvitationView,
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

    'DashboardView',
    'TrainingSessionView',
    'SubmitAnswerView',

    'TeacherStudentsView',
    'StudentDetailView',
    'StudentStatsView',

    'CreateInvitationView',
    'TeacherDashboardView',

    'CourseCreateView',
    'CourseAssignmentView',
    'CourseUpdateView',
    'CourseDeleteView',

    'UnitCreateView',
    'UnitUpdateView',
    'UnitDeleteView',
]