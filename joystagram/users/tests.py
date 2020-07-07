from model_bakery import baker
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import User, Profile
from munch import Munch

email = 'email@test.com'
password = '1234'
duplicated_email = 'duplicated_email@test.com'


class UserRegisterTestCase(APITestCase):
    url = '/api/users'

    def test_should_create(self):
        data = {
            'email': email,
            'password': password,
            'nickname': 'user_nick',
        }
        response = self.client.post(self.url, data)
        res = response.data
        self.assertEqual(201, response.status_code)
        self.assertEqual(res['email'], email)
        self.assertEqual(res['nickname'], data['nickname'])
        # self.assertEqual(res['introduce'], data['introduce'])
        # self.assertIsNotNone(res.get('profile'))
        # self.assertEqual(res['profile']['nickname'], data['profile']['nickname'])

    def test_without_email(self):
        response = self.client.post(self.url, {'email': '', 'password': password})
        self.assertEqual(400, response.status_code)

    def test_email_format(self):
        # wrong format
        wrong_email = 'wrong@format'
        response = self.client.post(self.url, {'email': wrong_email, 'password': password})
        self.assertEqual(400, response.status_code)

    def test_without_password(self):
        response = self.client.post(self.url, {'email': email, 'password': ''})
        self.assertEqual(400, response.status_code)

    def test_with_duplicated_email(self):
        self.user = baker.make(User, email=duplicated_email, password=password)
        response = self.client.post(self.url, {'email': duplicated_email, 'password': password})
        self.assertEqual(400, response.status_code)


class UserLoginTestCase(APITestCase):
    url = '/api/users/login'

    def setUp(self) -> None:
        self.user = baker.make(User, email=email, password=password)  # baker로 만들면 로그인 안됨..why

    def test_with_correct_info(self):
        response = self.client.post(self.url, {'email': email, 'password': password})
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.data.get('token'))
        self.assertIsNotNone(Token.objects.filter(user=self.user).exists())

    def test_without_password(self):
        response = self.client.post(self.url, {'email': email})
        self.assertEqual(400, response.status_code)

    def test_with_wrong_password(self):
        response = self.client.post(self.url, {'email': email, 'password': '1111'})
        self.assertEqual(400, response.status_code)

    def test_without_email(self):
        response = self.client.post(self.url, {'password': password})
        self.assertEqual(400, response.status_code)

    def test_with_wrong_email(self):
        response = self.client.post(self.url, {'email': 'wrong@email.com', 'password': password})
        self.assertEqual(400, response.status_code)


class UserLogoutTestCase(APITestCase):
    url = '/api/users/logout'

    def setUp(self) -> None:
        self.user = baker.make(User, email=email, password=password)
        token = baker.make(Token, user=self.user)
        self.client.force_authenticate(user=self.user, token=token)

    def test_should_delete_token(self):
        response = self.client.delete(self.url)
        self.assertEqual(200, response.status_code)
        self.assertFalse(Token.objects.filter(user_id=self.user.id).exists())


class UserDeactivateTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = baker.make(User, email=email, password=password)
        self.client.force_authenticate(user=self.user)
        self.url = f'/api/users/{self.user.id}/deactivate'

    def test_should_delete_user(self):
        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
        self.assertFalse(Token.objects.filter(user_id=self.user.id).exists())


class UserRetrieveTestCase(APITestCase):

    def setUp(self) -> None:
        self.data = {'password': '1111'}
        self.user = baker.make(User, email=email, password=password)
        self.token = baker.make(Token, user=self.user)
        self.url = f'/api/users/{self.user.id}'

    def test_should_retrieve_user(self):
        self.client.force_authenticate(user=self.user, token=self.token.key)
        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        res = Munch(response.data)
        self.assertTrue(res.id)
        self.assertEqual(res.id, self.user.id)
        self.assertEqual(res.email, email)

    def test_should_denied_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(401, response.status_code)


class UserUpdateTestCase(APITestCase):

    def setUp(self) -> None:
        self.data = {'password': '1111'}
        self.user = baker.make(User, email=email, password=password)
        self.token = baker.make(Token, user=self.user)
        self.url = f'/api/users/{self.user.id}/update_password'

    def test_should_update_password(self):
        self.client.force_authenticate(user=self.user, token=self.token.key)
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(200, response.status_code)

        # 비번변경 잘 되었는지 로그인해서 확인
        response = self.client.post('/api/users/login', {'email': email, 'password': '1111'})
        self.assertEqual(200, response.status_code, response.data)
        self.assertIsNotNone(response.data.get('token'))

    def test_should_denied_update(self):
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(401, response.status_code)
