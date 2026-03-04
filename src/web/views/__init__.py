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
]