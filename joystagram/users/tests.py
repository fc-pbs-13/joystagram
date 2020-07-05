from model_bakery import baker
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import User
from munch import Munch


class UserRegisterTestCase(APITestCase):
    url = '/api/users'
    email = "email@test.com"
    password = "1234"

    def test_should_create(self):
        self.email += '1'
        response = self.client.post(self.url, {"email": self.email, "password": self.password})
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['email'], self.email)

    def test_without_email(self):
        response = self.client.post(self.url, {"email": '', "password": self.password})
        self.assertEqual(400, response.status_code)

    def test_email_format(self):
        # wrong format
        wrong_email = 'wrong@format'
        response = self.client.post(self.url, {"email": wrong_email, "password": self.password})
        self.assertEqual(400, response.status_code)

    def test_without_password(self):
        response = self.client.post(self.url, {"email": self.email, "password": ''})
        self.assertEqual(400, response.status_code)


class UserLoginTestCase(APITestCase):
    url = '/api/users/login'
    email = "email@test.com"
    password = "1234"

    def setUp(self) -> None:
        self.email += '2'
        self.user = User.objects.create(email=self.email, password=self.password)

    def test_with_correct_info(self):
        response = self.client.post(self.url, {"email": self.email, "password": self.password})

        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.data.get('token'))
        self.assertIsNotNone(Token.objects.filter(user=self.user).exists())

    def test_without_password(self):
        response = self.client.post(self.url, {"email": self.email})
        self.assertEqual(400, response.status_code)

    def test_with_wrong_password(self):
        response = self.client.post(self.url, {"email": self.email, "password": "1111"})
        self.assertEqual(400, response.status_code)

    def test_without_email(self):
        response = self.client.post(self.url, {"password": self.password})
        self.assertEqual(400, response.status_code)

    def test_with_wrong_email(self):
        response = self.client.post(self.url, {"email": "wrong@email.com", "password": self.password})
        self.assertEqual(400, response.status_code)


class UserLogoutTestCase(APITestCase):
    url = '/api/users/logout'
    email = "email@test.com"
    password = "1234"

    def setUp(self) -> None:
        self.email += '3'
        self.user = baker.make(User, email=self.email, password=self.password)
        token = baker.make(Token, user=self.user)
        self.client.force_authenticate(user=self.user, token=token)

    def test_should_delete_token(self):
        response = self.client.delete(self.url)
        self.assertEqual(200, response.status_code)
        self.assertFalse(Token.objects.filter(user_id=self.user.id).exists())


class UserDeactivateTestCase(APITestCase):
    email = "email@test.com"
    password = "1234"

    def setUp(self) -> None:
        self.email += '4'
        self.user = User.objects.create(email=self.email, password=self.password)
        self.client.force_authenticate(user=self.user)
        self.url = f'/api/users/{self.user.id}/deactivate'

    def test_should_delete_user(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
        self.assertFalse(Token.objects.filter(user_id=self.user.id).exists())


class UserRetrieveUpdateTestCase(APITestCase):
    email = "email@test.com"
    password = "1234"

    def setUp(self) -> None:
        self.email += '5'
        self.user = baker.make(User, email=self.email, password=self.password)
        self.token = baker.make(Token, user=self.user)
        self.url = f'/api/users/{self.user.id}'

    def test_should_retrieve_user(self):
        self.client.force_authenticate(user=self.user, token=self.token.key)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        res = Munch(response.data)
        self.assertTrue(res.id)
        self.assertEqual(res.id, self.user.id)
        self.assertEqual(res.email, self.email)

    def test_should_update_password(self):
        data = {"password": '1111'}
        self.client.force_authenticate(user=self.user, token=self.token.key)
        response = self.client.patch(self.url, data=data)
        self.assertEqual(200, response.status_code)

        # 비번변경 잘 되었는지 로그인해서 확인
        response = self.client.post('/api/users/login', {"email": self.email, "password": '1111'})
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.data.get('token'))

    def test_should_denied_update(self):
        data = {"password": '1111'}
        response = self.client.patch(self.url, data=data)
        self.assertEqual(401, response.status_code)

    def test_should_denied_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)
