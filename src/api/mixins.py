from rest_framework.exceptions import PermissionDenied
from src.personal_forms.services import LearningUnitProgressService


class StudentAccessMixin:
    """
    Миксин для ViewSet-ов, которым нужно определять target_user (ученик или учитель).
    """
    def get_authorized_target_user(self):
        service = LearningUnitProgressService()
        student_id = self.request.query_params.get('student_id')

        try:
            return service.get_authorized_user(
                current_user=self.request.user,
                student_id=student_id
            )
        except (PermissionError, ValueError) as e:
            # Превращаем любую ошибку сервиса в 403 ошибку API
            raise PermissionDenied(str(e))