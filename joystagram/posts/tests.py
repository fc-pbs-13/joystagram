from model_bakery import baker
from rest_framework.test import APITestCase

from users.models import User

email = 'email@test.com'
password = '1234'
duplicated_email = 'duplicated_email@test.com'


class PostCreateTestCase(APITestCase):
    url = '/api/posts'

    def setUp(self) -> None:
        self.user = User.objects.create(email=email, password=password)

    def test_should_create(self):
        data = {
            'contents': 'yeeeeeeeeeee!!'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)
        res = response.data
        self.assertEqual(201, response.status_code)
        self.assertEqual(res['contents'], data['contents'])
        # self.assertEqual(res['nickname'], data['nickname'])

# class UserRetrieveTestCase(APITestCase):
#
#     def setUp(self) -> None:
#         self.data = {'password': '1111'}
#         self.user = baker.make(User, email=email, password=password)
#         self.token = baker.make(Token, user=self.user)
#         self.url = f'/api/users/{self.user.id}'
#
#     def test_should_retrieve_user(self):
#         self.client.force_authenticate(user=self.user, token=self.token.key)
#         response = self.client.get(self.url)
#
#         self.assertEqual(200, response.status_code)
#         res = Munch(response.data)
#         self.assertTrue(res.id)
#         self.assertEqual(res.id, self.user.id)
#         self.assertEqual(res.email, email)
#
#     def test_should_denied_retrieve(self):
#         response = self.client.get(self.url)
#         self.assertEqual(401, response.status_code)
#
#
# class UserUpdateTestCase(APITestCase):
#
#     def setUp(self) -> None:
#         self.data = {'password': '1111'}
#         self.user = baker.make(User, email=email, password=password)
#         self.token = baker.make(Token, user=self.user)
#         self.url = f'/api/users/{self.user.id}/update_password'
#
#     def test_should_update_password(self):
#         self.client.force_authenticate(user=self.user, token=self.token.key)
#         response = self.client.patch(self.url, data=self.data)
#         self.assertEqual(200, response.status_code)
#
#         # 비번변경 잘 되었는지 로그인해서 확인
#         response = self.client.post('/api/users/login', {'email': email, 'password': '1111'})
#         self.assertEqual(200, response.status_code)
#         self.assertIsNotNone(response.data.get('token'))
#
#     def test_should_denied_update(self):
#         response = self.client.patch(self.url, data=self.data)
#         self.assertEqual(401, response.status_code)
