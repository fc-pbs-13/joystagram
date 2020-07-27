from django.db.models import Q
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from taggit.models import Tag
from core.tests import TempFileMixin
from likes.models import PostLike
from posts.models import Post
from relationships.models import Follow

INVALID_ID = -1


class PostCreateTestCase(APITestCase, TempFileMixin):
    """게시글 생성 테스트"""
    url = '/api/posts'

    def setUp(self) -> None:
        self.tags = ['ttt', 'ggg']
        self.data = {
            'photos': self.generate_photo_file(),
            'content': 'hello joystagram!',
            'tags': str(self.tags).replace("'", '"')  # '["ttt", "ggg", "ggg"]'
        }
        self.multiple_data = {
            'photos': [self.generate_photo_file(), self.generate_photo_file()],
            'content': 'hello joystagram!',
            'tags': str(self.tags).replace("'", '"')
        }
        self.user = baker.make('users.User')
        self.profile = baker.make('users.Profile', user=self.user, nickname='test_user')

    def test_should_create(self):
        """생성-성공: 단일 이미지"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            self.data,
            format='multipart',
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
        self.assertEqual(res['tags'], self.tags)

    def test_should_denied401(self):
        """생성-인증 필요"""
        response = self.client.post(
            self.url,
            encode_multipart(BOUNDARY, self.data),
            content_type=MULTIPART_CONTENT
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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


class PostListTestCase(APITestCase):
    """내가 팔로우하는 유저들의 게시글 리스트"""

    def setUp(self) -> None:
        users = baker.make('users.User', _quantity=4)
        posts = []
        for user in users:
            self.profile = baker.make('users.Profile', user=user)
            posts += baker.make('posts.Post', owner=user, _quantity=2)

        for post in posts:
            baker.make('comments.Comment', post=post, _quantity=2)
        baker.make('relationships.Follow', owner=users[0], to_user=users[1])
        baker.make('relationships.Follow', owner=users[0], to_user=users[2])
        baker.make('relationships.Follow', owner=users[1], to_user=users[0])

        self.tags = ['django', 'django rest framework', 'python', 'python programming', 'java']
        posts[0].tags.add(self.tags[0])
        posts[1].tags.add(self.tags[0], self.tags[1])
        posts[2].tags.add(self.tags[0], self.tags[1])
        posts[3].tags.add(self.tags[1], self.tags[3])
        posts[4].tags.add(self.tags[0], self.tags[1], self.tags[2])
        self.user = users[0]
        self.tag = Tag.objects.get(name=self.tags[0])

    def test_should_list_posts(self):
        """리스트-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/posts')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        res = response.data

        post_list = Post.objects.filter(
            Q(owner_id__in=Follow.objects.filter(owner=self.user).values('to_user_id')) |
            Q(owner=self.user)
        ).order_by('-id')
        self.assertEqual(len(res['results']), len(post_list))

        for post_res, post_obj in zip(res['results'], post_list):
            self.assertEqual(post_res.get('id'), post_obj.id)
            self.assertEqual(post_res.get('content'), post_obj.content)
            self.assertIsNotNone(post_res.get('_photos'))
            self.assertEqual(post_res.get('likes_count'), post_obj.likes.count())
            self.assertEqual(post_res.get('comments_count'), post_obj.comments.count())
            if post_res.get('like_id'):
                self.assertIsNotNone(PostLike.objects.get(id=post_res.get('like_id')).post, post_res)
            for photos in post_res.get('_photos'):
                self.assertTrue(photos.get('img').endswith('jpg'))

    def test_tagged_post_list(self):
        """태그를 가진 포스트 검색"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/tags/{self.tag.id}/posts')
        res = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)

        for post in res:
            self.assertTrue(self.tag.name in post['tags'])

    def test_tagged_post_list_invalid_tag_id(self):
        """포스트 검색-유효하지 않은 태그id"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/tags/{INVALID_ID}/posts')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_search_tag_list(self):
        """검색어로 태그 검색"""
        self.client.force_authenticate(user=self.user)
        search_str = 'd'
        response = self.client.get(f'/api/tags?name={search_str}')
        res = response.data['results']
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)

        tag_list = Tag.objects.filter(name__icontains=search_str).order_by('-id')  # .distinct()
        self.assertEqual(len(res), len(tag_list))
        for tag_res, tag_obj in zip(res, tag_list):
            self.assertEqual(tag_res['id'], tag_obj.id)
            self.assertEqual(tag_res['name'], tag_obj.name)
