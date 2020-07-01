from model_bakery import baker
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import User
from munch import Munch

email = "email@test.com"
password = "1234"


class UserRegisterTestCase(APITestCase):
    url = '/api/users'

    def test_should_create(self):
        response = self.client.post(self.url, {"email": email, "password": password})
        self.assertEqual(201, response.status_code)
        self.assertEqual(response.data['email'], email)

    # def test_without_email(self):
    #     response = self.client.post(self.url, {"email": '', "password": password})
    #     self.assertEqual(400, response.status_code)
    #
    # def test_email_format(self):
    #     # wrong format
    #     wrong_email = 'wrong@format'
    #     response = self.client.post(self.url, {"email": wrong_email, "password": password})
    #     self.assertEqual(400, response.status_code)
    #
    # def test_without_password(self):
    #     response = self.client.post(self.url, {"email": email, "password": ''})
    #     self.assertEqual(400, response.status_code)


class UserLoginTestCase(APITestCase):
    url = '/api/users/login'

    def setUp(self) -> None:
        self.user = User.objects.create(email=email)
        self.user.set_password(password)
        self.user.save()

    def test_with_correct_info(self):
        response = self.client.post(self.url, {"email": email, "password": password})
        print(response.data)
        self.assertEqual(200, response.status_code)

    # def test_is_token_created(self):
    #     response = self.client.post(self.url, {"email": email, "password": password})
    #     print(response.data)
    #     self.assertEqual(200, response.status_code)
    #     self.assertTrue(response.data['token'])
    #     # self.assertTrue(Token.objects.get(user=self.user))
    #     self.assertTrue(Token.objects.filter(user_id=self.user.id).exists())

#     def test_without_password(self):
#         response = self.client.post(self.url, {"email": email})
#         self.assertEqual(400, response.status_code)
#
#     def test_with_wrong_password(self):
#         response = self.client.post(self.url, {"email": email, "password": "1111"})
#         self.assertEqual(404, response.status_code)
#
#     def test_without_email(self):
#         response = self.client.post(self.url, {"password": password})
#         self.assertEqual(400, response.status_code)
#
#     def test_with_wrong_email(self):
#         response = self.client.post(self.url, {"email": "wrong@email.com", "password": password})
#         self.assertEqual(404, response.status_code)
#
#     def test_with_correct_info(self):
#         response = self.client.post(self.url, {"email": email, "password": password})
#         self.assertEqual(200, response.status_code)
#
#
#
# class UserLogoutTestCase(APITestCase):
#     url = '/api/users/logout'
#
#     def setUp(self) -> None:
#         self.user = User.objects.create(email=email)
#         self.user.set_password(password)
#         self.user.save()
#         # Get token by login
#         baker.make(Token, user=self.user)
#         token = Token.objects.get(user_id=self.user.id)
#         self.client.force_authenticate(user=self.user, token=token)
#
#     def test_is_token_deleted(self):
#         response = self.client.delete(self.url)
#         self.assertEqual(200, response.status_code)
#         self.assertFalse(Token.objects.filter(user_id=self.user.id).exists())
#
#
# class UserDeactivateTestCase(APITestCase):
#
#     def setUp(self) -> None:
#         self.user = User.objects.create(email=email)
#         self.user.set_password(password)
#         self.user.save()
#         self.client.force_authenticate(user=self.user)
#         self.url = f'/api/users/{self.user.id}/deactivate'
#
#     def test_user_deleted(self):
#         response = self.client.delete(self.url)
#         self.assertEqual(204, response.status_code)
#         self.assertFalse(User.objects.filter(id=self.user.id).exists())
#         self.assertFalse(Token.objects.filter(user_id=self.user.id).exists())
#
#
# class UserRetrieveUpdateTestCase(APITestCase):
#
#     def setUp(self) -> None:
#         self.user = User.objects.create(email=email)
#         self.user.set_password(password)
#         self.user.save()
#
#         self.client.force_authenticate(user=self.user)
#         self.url = f'/api/users/{self.user.id}'
#
#     def test_user_retrieve(self):
#         response = self.client.get(self.url)
#         self.assertEqual(200, response.status_code)
#
#         res = Munch(response.data)
#         self.assertTrue(res.id)
#         self.assertEqual(res.id, self.user.id)
#         self.assertEqual(res.email, email)
#
#     def test_user_update(self):
#         data = {
#             "phoneNum": "010-1234-5678",
#             "plateNum": "1243",
#             "cardNum": "3072-1730-7021-1331",
#             "username": "user22",
#         }
#         response = self.client.put(self.url, data=data)
#         self.assertEqual(200, response.status_code)
#
#         res = Munch(response.data)
#         self.assertEqual(res.username, data['username'])
#         self.assertEqual(res.plateNum, data['plateNum'])
#         self.assertEqual(res.cardNum, data['cardNum'])
