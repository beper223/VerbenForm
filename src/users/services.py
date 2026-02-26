import secrets
import string

from src.users.models import StudentInvitation


class InvitationService:
    @staticmethod
    def create_invitation(teacher, email):
        # Генерируем читаемый код: заглавные буквы и цифры
        alphabet = string.ascii_uppercase + string.digits
        code = ''.join(secrets.choice(alphabet) for _ in range(8))

        invitation = StudentInvitation.objects.create(
            teacher=teacher,
            email=email,
            code=code
        )
        # Здесь можно вызвать функцию отправки email:
        # send_invitation_email(email, code)
        return invitation