import secrets
import string
from django.core.mail import send_mail
from django.conf import settings
from src.users.models import StudentInvitation


class InvitationService:
    @staticmethod
    def generate_code():
        # Генерируем красивый код: 8 символов (буквы и цифры)
        chars = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(chars) for _ in range(8))

    @classmethod
    def create_invitation(cls, teacher, email):
        code = cls.generate_code()

        invitation = StudentInvitation.objects.create(
            teacher=teacher,
            email=email,
            code=code
        )
        # Здесь можно вызвать функцию отправки email:
        # send_invitation_email(email, code)
        return invitation

    @classmethod
    def send_invitation(cls, teacher, email):
        invitation = cls.create_invitation(teacher, email)

        # 2. Отправляем email (настройка SMTP должна быть в settings.py)
        subject = "Приглашение на платформу изучения немецкого"
        message = (
            f"Здравствуйте! Ваш преподаватель {teacher.username} пригласил вас на платформу.\n"
            f"Ваш код для первого входа: {invitation.code}\n"
            f"Зарегистрируйтесь по ссылке: https://your-app.com/activate?code={invitation.code}"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        return invitation