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
    email = "email@test.com"
    password = "1234"

    def setUp(self) -> None:
        # self.email += '1'
        response = self.client.post('/api/users', {"email": self.email, "password": self.password})
        # self.user = User.objects.create(email=self.email)
        self.user = User.objects.get(email=self.email)
        # self.user.save()

    def test_with_correct_info(self):
        response = self.client.post(self.url, {"email": self.email, "password": self.password})

        user = User.objects.get(email=self.email)
        print(response.data)
        print(self.email, self.password)
        print(user.email, user.password)
        from django.contrib.auth import authenticate
        user = authenticate(email=self.email, password=self.password)  # request=self.request,
        print(user)

        self.assertEqual(200, response.status_code)
        self.assertTrue(response.data['token'])
        self.assertTrue(Token.objects.get(user=self.user))
        self.assertTrue(Token.objects.filter(user_id=self.user.id).exists())

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
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()
        # Get token by login
        baker.make(Token, user=self.user)
        token = Token.objects.get(user_id=self.user.id)
        self.client.force_authenticate(user=self.user, token=token)

    def test_is_token_deleted(self):
        response = self.client.delete(self.url)
        self.assertEqual(200, response.status_code)
        self.assertFalse(Token.objects.filter(user_id=self.user.id).exists())


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


class UserRetrieveUpdateTestCase(APITestCase):
    email = "email@test.com"
    password = "1234"

    def setUp(self) -> None:
        self.email += '1'
        self.user = User.objects.create(email=self.email)
        self.user.set_password(self.password)
        self.user.save()

        self.client.force_authenticate(user=self.user)
        self.url = f'/api/users/{self.user.id}'

    def test_user_retrieve(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

        res = Munch(response.data)
        self.assertTrue(res.id)
        self.assertEqual(res.id, self.user.id)
        self.assertEqual(res.email, self.email)

    def test_user_update(self):
        data = {
            "password": 1234
        }
        response = self.client.patch(self.url, data=data)
        self.assertEqual(200, response.status_code)

        res = Munch(response.data)
        # self.assertEqual(res.username, data[''])
