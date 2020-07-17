import io
from PIL import Image
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from likes.models import PostLike


class PostCreateTestCase(APITestCase):
    """게시글 생성 테스트"""
    url = '/api/posts'

    @staticmethod
    def generate_photo_file():
        """업로드 테스트용 사진 파일 생성"""
        file = io.BytesIO()
        image = Image.new('RGBA', size=(1, 1), color=(0, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def setUp(self) -> None:
        self.data = {
            'photos': self.generate_photo_file(),
            'content': 'hello joystagram!'
        }
        self.multiple_data = {
            'photos': [self.generate_photo_file(), self.generate_photo_file()],
            'content': 'hello joystagram!'
        }
        self.user = baker.make('users.User')
        self.profile = baker.make('users.Profile', user=self.user, nickname='test_user')

    def test_should_create(self):
        """생성-성공: 단일 이미지"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            self.data,
            format='multipart'
        )
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)
        self.assertEqual(res['content'], self.data['content'])

    def test_should_create_multiple(self):
        """생성-성공: 다중 이미지"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            self.multiple_data,
            format='multipart'
        )
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)
        self.assertEqual(res['content'], self.multiple_data['content'])
        self.assertEqual(len(res['_photos']), len(self.multiple_data['photos']))

    def test_should_denied401(self):
        """생성-인증 필요"""
        response = self.client.post(
            self.url,
            encode_multipart(BOUNDARY, self.data),
            content_type=MULTIPART_CONTENT
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PostListTestCase(APITestCase):
    """게시물 리스트 테스트"""
    url = f'/api/posts'

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.profile = baker.make('users.Profile', user=self.user)
        self.posts = baker.make('posts.Post', owner=self.user, _quantity=2)
        self.img_url = 'post_image/test.png'
        self.likes_count = 3
        self.comments_count = 2
        for post in self.posts:
            baker.make('posts.Photo', post=post, img=self.img_url, _quantity=2)
            self.post_likes = baker.make('likes.PostLike', post=post, _quantity=self.likes_count)
            self.post_likes = baker.make('comments.Comment', post=post, _quantity=self.comments_count)

    def test_should_list_posts(self):
        """리스트-성공"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.data
        for post in res['results']:
            self.assertIsNotNone(post.get('id'))
            self.assertIsNotNone(post.get('content'))
            self.assertIsNotNone(post.get('_photos'))
            self.assertIsNotNone(post.get('comments_count'))
            self.assertIsNotNone(post.get('likes_count'))
            self.assertEqual(post.get('comments_count'), self.comments_count)
            if post.get('like_id'):
                self.assertIsNotNone(PostLike.objects.get(id=post.get('like_id')).post, post)
            for photos in post.get('_photos'):
                self.assertTrue(photos.get('img').endswith(self.img_url))


class PostRetrieveTestCase(APITestCase):
    """게시글 조회 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user, nickname='test_user')
        post = baker.make('posts.Post', owner=self.user)
        baker.make('comments.Comment', post=post, _quantity=2)
        self.url = f'/api/posts/{post.id}'

    def test_should_retrieve_post(self):
        """조회-성공"""
        response = self.client.get(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.assertIsNotNone(res.get('id'))
        self.assertIsNotNone(res.get('content'))


class PostUpdateDeleteTestCase(APITestCase):
    """게시글 수정, 삭제 테스트"""

    def setUp(self) -> None:
        self.data = {'content': '1111'}
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user)
        post = baker.make('posts.Post', owner=self.user)
        self.likes_count = 3
        baker.make('likes.PostLike', post=post, _quantity=self.likes_count)
        self.url = f'/api/posts/{post.id}'

    def test_should_update(self):
        """수정-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data=self.data)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.assertEqual(res['content'], self.data['content'])

    def test_should_denied_update401(self):
        """수정-인증 필요"""
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_should_denied_update403(self):
        """수정-권한 없음"""
        invalid_user = baker.make('users.User')
        baker.make('users.Profile', user=invalid_user)
        self.client.force_authenticate(user=invalid_user)
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def test_should_delete(self):
        """삭제-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

    def test_should_denied_delete401(self):
        """삭제-인증 필요"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_should_denied_delete403(self):
        """삭제-권한 없음"""
        invalid_user = baker.make('users.User')
        baker.make('users.Profile', user=invalid_user)
        self.client.force_authenticate(user=invalid_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
