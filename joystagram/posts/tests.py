import io

from PIL import Image
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Comment

email = 'email@test.com'
password = '1234'
duplicated_email = 'duplicated_email@test.com'


class PostCreateTestCase(APITestCase):
    url = '/api/posts'

    def generate_photo_file(self):
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
        self.assertEqual(res['content'], self.data['content'])
        # TODO 이미지 업로드 되었는지도 테스트 추가


class PostListTestCase(APITestCase):
    """게시물 리스트 테스트"""
    url = f'/api/posts'

    def setUp(self) -> None:
        self.users = []
        for i in range(1, 4):
            self.user = baker.make('users.User', email=f'{email}{i}', password=password)
            self.users.append(self.user)
            self.profile = baker.make('users.Profile', user=self.user, nickname=f'test_user{i}')
            self.posts = baker.make('posts.Post', content='우리 인생 화이팅...!',
                                    owner=self.profile, _quantity=3)
            for post in self.posts:
                # TODO Photo이미지 생성..?
                baker.make('posts.Photo', post=post, img='post_image/test.png', _quantity=3)

    def test_should_list_posts(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.data
        for post in res:
            self.assertIsNotNone(post.get('id'))
            self.assertIsNotNone(post.get('content'))
            self.assertIsNotNone(post.get('photos'))
            for photos in post.get('photos'):
                self.assertIsNotNone(photos.get('img'))


class PostRetrieveTestCase(APITestCase):
    """게시글 조회 테스트"""

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
        self.assertIsNotNone(res.get('id'))
        self.assertIsNotNone(res.get('content'))

    # def test_should_denied_retrieve(self):
    #     """차단"""
    #     response = self.client.get(self.url)
    #     self.assertEqual(401, response.status_code)


class PostUpdateTestCase(APITestCase):

    def setUp(self) -> None:
        self.data = {'content': '1111'}
        self.user = baker.make('users.User', email=email, password=password)
        profile = baker.make('users.Profile', user=self.user)
        post = baker.make('posts.Post', owner=profile)
        self.url = f'/api/posts/{post.id}'

    def test_should_update(self):
        """업데이트 성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data=self.data)
        res = response.data
        self.assertEqual(200, response.status_code, res)
        self.assertEqual(res['content'], self.data['content'])

    def test_should_denied(self):
        """권한 없음"""
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(401, response.status_code)


class CommentCreateTestCase(APITestCase):
    """댓글 생성 테스트"""

    def setUp(self) -> None:
        self.data = {
            'content': 'hello joy This is Comment!!'
        }
        self.user = baker.make('users.User', email=email, password=password)
        profile = baker.make('users.Profile', user=self.user, nickname='test_user')
        post = baker.make('posts.Post', content='우리 인생 화이팅...!', owner=profile)
        baker.make('posts.Photo', post=post, img='post_image/test.png')
        self.url = f'/api/posts/{post.id}/comments'

    def test_should_create(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=self.data)
        res = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)
        self.assertEqual(res['content'], self.data['content'])
        self.assertIsNotNone(res.get('post_id'))

        owner = res.get('owner')
        self.assertIsNotNone(owner)
        self.assertIsNotNone(owner.get('id'))
        self.assertIsNotNone(owner.get('nickname'))

        recomments = res.get('recomments')
        self.assertIsNotNone(recomments)
        for recomment in recomments:
            self.assertIsNotNone(recomment)
            self.assertIsNotNone(recomment.get())
        self.assertTrue(Comment.objects.filter(id=res.get('id')).exists())


class CommentListTestCase(APITestCase):
    """댓글 리스트 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User', email=email, password=password)
        profile = baker.make('users.Profile', user=self.user, nickname='test_user')
        post = baker.make('posts.Post', owner=profile)
        baker.make('posts.Comment', post=post, _quantity=3)
        self.url = f'/api/posts/{post.id}/comments'

    def test_should_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        res = response.data
        for comment in res:
            self.assertIsNotNone(comment['id'])
            self.assertIsNotNone(comment['content'])
            self.assertIsNotNone(comment['owner'])
            self.assertIsNotNone(comment['post_id'])


class ReCommentCreateTestCase(APITestCase):
    """대댓글 생성 테스트"""

    def setUp(self):
        self.user = baker.make('users.User', email=email, password=password)
        baker.make('users.Profile', user=self.user, nickname='test_user')
        self.comment = baker.make('posts.Comment')

    def test_should_create(self):
        data = {"content": "blah"}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/comments/{self.comment.id}/recomments', data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        res = response.data
        self.assertIsNotNone(res['id'])
        self.assertIsNotNone(res['content'])
        self.assertIsNotNone(res['owner'])
