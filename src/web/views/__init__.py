from src.web.views.home import HomeView
from src.web.views.users import (
    UserLoginView,
    UserRegisterView,
    ProfileView,
    MyPasswordChangeView,
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
    VerbLookupView,
)

from src.web.views.vocab import (
    VerbGroupCreateView,
    VerbGroupUpdateView,
    VerbGroupDeleteView,
)

from src.web.views.legal import (
    ImpressumView,
    PrivacyView,
)

from src.web.views.my_markdown import markdown_page

__all__ = [
    'UserLoginView',
    'UserRegisterView',
    'ProfileView',
    'MyPasswordChangeView',

    'TrainingSessionView',
    'SubmitAnswerView',

    'StudentDetailView',
    'StudentCourseDetailView',
    'UnitStatsView',

    'CreateInvitationView',
    'InvitationUpdateView',
    'InvitationDeleteView',
    'TeacherDashboardView',
    'HomeView',

    'CourseListView',
    'CourseDetailView',
    'CourseCreateView',
    'CourseAssignmentView',
    'CourseUpdateView',
    'CourseDeleteView',

    'UnitCreateView',
    'UnitUpdateView',
    'UnitDeleteView',
    'VerbLookupView',

    'VerbGroupCreateView',
    'VerbGroupUpdateView',
    'VerbGroupDeleteView',

    'ImpressumView',
    'PrivacyView',
    'markdown_page',
]