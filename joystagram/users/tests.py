from model_bakery import baker
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import User

email = 'email@test.com'
password = '1234'


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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res['email'], email)
        self.assertEqual(res['nickname'], data['nickname'])
        self.assertTrue('introduce' in res)
        self.assertTrue('img' in res)

    def test_without_email(self):
        response = self.client.post(self.url, {'email': '', 'password': password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_format(self):
        wrong_email = 'wrong@format'
        response = self.client.post(self.url, {'email': wrong_email, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_password(self):
        response = self.client.post(self.url, {'email': email, 'password': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_duplicated_email(self):
        duplicated_email = 'duplicated_email@test.com'
        self.user = baker.make(User, email=duplicated_email, password=password)
        response = self.client.post(self.url, {'email': duplicated_email, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTestCase(APITestCase):
    url = '/api/users/login'

    def setUp(self) -> None:
        self.user = baker.make(User, email=email, password=password)  # baker로 만들면 로그인 안됨..why

    def test_with_correct_info(self):
        response = self.client.post(self.url, {'email': email, 'password': password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)
        self.assertTrue(Token.objects.filter(user=self.user, key=response.data['token']).exists())

    def test_without_password(self):
        response = self.client.post(self.url, {'email': email})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_wrong_password(self):
        response = self.client.post(self.url, {'email': email, 'password': '1111'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_without_email(self):
        response = self.client.post(self.url, {'password': password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_wrong_email(self):
        response = self.client.post(self.url, {'email': 'wrong@email.com', 'password': password})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTestCase(APITestCase):
    url = '/api/users/logout'

    def setUp(self) -> None:
        self.user = baker.make(User, email=email, password=password)
        self.token = baker.make(Token, user=self.user)

    def test_should_delete_token(self):
        self.client.force_authenticate(user=self.user, token=self.token)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user_id=self.user.id).exists())

    def test_should_denied_delete_token(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(Token.objects.filter(user_id=self.user.id).exists())


class UserDeactivateTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = baker.make(User, email=email, password=password)
        self.client.force_authenticate(user=self.user)
        self.url = f'/api/users/{self.user.id}'

    def test_should_delete_user(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())


class UserRetrieveTestCase(APITestCase):

    def setUp(self) -> None:
        self.data = {'password': '1111'}
        self.user = baker.make(User, email=email, password=password)
        self.token = baker.make(Token, user=self.user)
        self.url = f'/api/users/{self.user.id}'

    def test_should_retrieve_user(self):
        self.client.force_authenticate(user=self.user, token=self.token.key)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.data
        self.assertTrue(res['id'])
        self.assertEqual(res['id'], self.user.id)
        self.assertEqual(res['email'], email)
        self.assertTrue('introduce' in res)
        self.assertTrue('img' in res)

    def test_should_denied_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserListTestCase(APITestCase):

    def setUp(self) -> None:
        users = baker.make('users.User', _quantity=5)
        for i in range(len(users)):
            baker.make('users.profile', user=users[i], nickname=f'user{i}')
        self.user = users[0]

    def test_should_list_user(self):
        self.client.force_authenticate(user=self.user)
        search_nick = '1'
        response = self.client.get(f'/api/users?nickname={search_nick}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user_res in response.data['results']:
            self.assertTrue('img' in user_res)
            nick = user_res['nickname']
            self.assertTrue(search_nick in nick or search_nick.capitalize() in nick)


class UserUpdateTestCase(APITestCase):

    def setUp(self) -> None:
        self.data = {'password': '1111'}
        self.profile_data = {
            'nickname': 'new_nickname',
            'introduce': 'new_introduce'
        }
        self.user = baker.make('users.User', email=email, password=password)
        baker.make('users.Profile', user=self.user)
        self.password_url = f'/api/users/{self.user.id}/update_password'
        self.url = f'/api/users/{self.user.id}'

    def test_should_update_password(self):
        """비밀번호 수정-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.password_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 비번변경 잘 되었는지 로그인해서 확인
        response = self.client.post('/api/users/login', {'email': email, 'password': '1111'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

    def test_should_denied_update_password(self):
        """비밀번호 수정-권한 없음"""
        response = self.client.patch(self.password_url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_update_profile(self):
        """프로필 수정-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data=self.profile_data)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('id' in res)
        self.assertTrue('email' in res)
        self.assertTrue('img' in res)
        self.assertEqual(self.profile_data['nickname'], res['nickname'])
        self.assertEqual(self.profile_data['introduce'], res['introduce'])

    def test_should_denied_update_profile(self):
        """프로필 수정-권한 없음"""
        response = self.client.patch(self.url, data=self.profile_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
