from model_bakery import baker
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
import io
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from posts.models import Post
from users.models import User, Profile

email = 'email@test.com'
password = '1234'
duplicated_email = 'duplicated_email@test.com'


class PostCreateTestCase(APITestCase):
    url = '/api/posts'

    def generate_photo_file(self):
        """업로드 테스트용 사진 파일 생성"""
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def setUp(self) -> None:
        self.data = {
            'photos': self.generate_photo_file(),
            'contents': 'hello joystagram!'
        }
        self.user = baker.make('users.User', email=email, password=password)
        self.profile = baker.make('users.Profile', user=self.user, nickname='test_user')

    def test_should_create(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            encode_multipart(BOUNDARY, self.data),
            content_type=MULTIPART_CONTENT
        )
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)
        self.assertEqual(res['contents'], self.data['contents'])
        # TODO 이미지 업로드 되었는지도 테스트 추가


class PostRetrieveTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = baker.make('users.User', email=email, password=password)
        self.profile = baker.make('users.Profile', user=self.user, nickname='test_user')
        self.post = baker.make('posts.Post', owner=self.profile)
        self.url = f'/api/posts/{self.post.id}'

    def test_should_retrieve_post(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.data
        print(res)
        self.assertIsNotNone(res.get('id'))
        self.assertIsNotNone(res.get('contents'))

    # 권한
    # def test_should_denied_retrieve(self):
    #     response = self.client.get(self.url)
    #     self.assertEqual(401, response.status_code)

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
