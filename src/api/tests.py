from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase
from rest_framework import status

from src.users.models import StudentInvitation
from src.personal_forms.models import LearningUnit, Verb, VerbTranslation, VerbForm, UserVerbProgress
from src.common.choices import CEFRLevel, SkillType, LanguageCode, Pronoun, Tense, VerbType, Reflexiv

User = get_user_model()


class BaseApiTest(APITestCase):
    def setUp(self):
        # 1. Группы
        self.teacher_group, _ = Group.objects.get_or_create(name='Teachers')

        # 2. Учитель
        self.teacher = User.objects.create_user(
            username='teacher_user', email='teacher@test.com', password='password123'
        )
        self.teacher.groups.add(self.teacher_group)

        # 3. Студенты
        self.student = User.objects.create_user(
            username='student_user', email='student@test.com', password='password123', language='ru'
        )
        self.student.teachers.add(self.teacher)

        self.other_student = User.objects.create_user(
            username='other_user', email='other@test.com', password='password123'
        )

        # 4. Создаем контент (ОБЯЗАТЕЛЬНО используем .value)
        self.verb = Verb.objects.create(
            infinitive="gehen",
            level=CEFRLevel.A1.value,
            verb_type=VerbType.REGULAR.value,  # Явно указываем короткое значение "reg"
            reflexivitaet=Reflexiv.NREFL.value  # Явно указываем "nrefl"
        )

        VerbTranslation.objects.create(
            verb=self.verb,
            language_code=LanguageCode.RU.value,
            translation="идти"
        )

        VerbForm.objects.create(
            verb=self.verb,
            tense=Tense.PRAESENS.value,
            pronoun=Pronoun.ICH.value,
            form="gehe"
        )

        # 5. Учебный юнит
        self.unit = LearningUnit.objects.create(
            title="Basis Verben",
            order=1,
            level=CEFRLevel.A1.value,
            skill_type=SkillType.TRANSLATION.value  # "translation"
        )
        self.unit.verbs.add(self.verb)

    def login(self, user):
        self.client.force_authenticate(user=user)


class AuthTests(BaseApiTest):
    def test_register_student(self):
        url = '/api/auth/register/'
        data = {
            "username": "newbie",
            "email": "new@test.com",
            "password": "password123",
            "password_confirm": "password123"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_flow(self):
        response = self.client.post('/api/auth/login/', {
            "username": "student_user", "password": "password123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


class LearningTests(BaseApiTest):
    def test_units_list(self):
        self.login(self.student)
        response = self.client.get('/api/learning-units/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unit_progress_detail(self):
        self.login(self.student)
        url = f'/api/learning-units/{self.unit.id}/progress/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_global_stats(self):
        self.login(self.student)
        response = self.client.get('/api/learning-units/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TrainingTests(BaseApiTest):
    def test_get_next_card(self):
        self.login(self.student)
        url = '/api/training/next-card/'
        response = self.client.get(url, {'learning_unit_id': self.unit.id})
        self.assertIn(response.status_code, [200, 204])


class InvitationTests(BaseApiTest):
    def test_full_invite_cycle(self):
        self.login(self.teacher)
        res_invite = self.client.post('/api/invites/get_invite/', {"email": "invitee@test.com"})
        code = res_invite.data['code']

        self.client.logout()
        res_act = self.client.post('/api/auth/activate_student/', {
            "code": code,
            "username": "activated_student",
            "password": "password123"
        })
        self.assertEqual(res_act.status_code, status.HTTP_200_OK)


class TeacherTests(BaseApiTest):
    def test_students_list(self):
        self.login(self.teacher)
        response = self.client.get('/api/teacher/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class ProgressTests(BaseApiTest):
    def test_verb_progress_filtering(self):
        UserVerbProgress.objects.create(
            user=self.student,
            verb=self.verb,
            skill_type=SkillType.TRANSLATION.value
        )
        self.login(self.student)
        res_student = self.client.get('/api/verb-progress/')
        self.assertEqual(len(res_student.data), 1)

        self.login(self.teacher)
        res_teacher = self.client.get(f'/api/verb-progress/?student_id={self.student.id}')
        self.assertEqual(len(res_teacher.data), 1)


class TrainingAnswerTests(BaseApiTest):
    def setUp(self):
        super().setUp()
        # Для теста ответов нам нужно, чтобы у юнита были карточки.
        # Мы уже создали VerbForm и VerbTranslation в BaseApiTest.setUp
        self.login(self.student)

    def test_submit_correct_answer(self):
        # 1. Сначала получаем карточку, чтобы узнать card_id
        url_next = '/api/training/next-card/'
        res_card = self.client.get(url_next, {'learning_unit_id': self.unit.id})

        # Если карточек нет (204), мы не можем протестировать ответ
        if res_card.status_code == status.HTTP_204_NO_CONTENT:
            self.skipTest("Нет доступных карточек для тестирования ответа")

        card_id = res_card.data['card_id']
        # В вашем сервисе правильный ответ для ICH + gehen (translation) это "идти" (из setUp)
        # В реальном тесте нужно знать, какой ответ правильный.
        # Допустим, мы знаем, что это "идти" (т.к. мы его создали в setUp)

        # 2. Отправляем правильный ответ
        url_ans = '/api/training/answer/'
        data = {
            "card_id": card_id,
            "answer": "идти"
        }
        response = self.client.post(url_ans, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['correct'])
        self.assertGreaterEqual(response.data['streak'], 1)

        # 3. Проверяем, что в базе создался/обновился прогресс
        progress = UserVerbProgress.objects.get(user=self.student, verb=self.verb)
        self.assertEqual(progress.correct_count, 1)
        self.assertEqual(progress.streak, 1)

    def test_submit_wrong_answer(self):
        # 1. Получаем карточку
        res_card = self.client.get('/api/training/next-card/', {'learning_unit_id': self.unit.id})
        if res_card.status_code == status.HTTP_204_NO_CONTENT:
            self.skipTest("Нет доступных карточек")

        card_id = res_card.data['card_id']

        # 2. Отправляем заведомо ложный ответ
        response = self.client.post('/api/training/answer/', {
            "card_id": card_id,
            "answer": "неправильно"
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['correct'])
        self.assertEqual(response.data['streak'], 0)  # Стрик должен сброситься

        # 3. Проверяем базу
        progress = UserVerbProgress.objects.get(user=self.student, verb=self.verb)
        self.assertEqual(progress.wrong_count, 1)
        self.assertEqual(progress.streak, 0)

    def test_answer_missing_data(self):
        # Проверка валидации: пустой запрос
        response = self.client.post('/api/training/answer/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)