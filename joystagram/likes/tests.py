from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase


class PostLikeTestCase(APITestCase):
    """게시글 좋아요 생성, 삭제 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.profile = baker.make('users.Profile', user=self.user, nickname='test_user')
        self.post = baker.make('posts.Post')
        self.url = f'/api/posts/{self.post.id}/post_likes'

    def test_should_create(self):
        """생성-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)

    def test_should_denied_duplicate_likes(self):
        """생성-중복 차단"""
        baker.make('likes.PostLike', owner=self.profile, post=self.post)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, res)

    def test_should_denied_create_401(self):
        """생성-인증 필요"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_should_denied_invalid_post_id(self):
        """생성-유효하지 않은 post_id"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/posts/{self.post.id + 1}/post_likes')
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, res)

    def test_should_delete(self):
        """삭제-성공"""
        post_like = baker.make('likes.PostLike', owner=self.profile, post=self.post)
        self.url = f'/api/posts/{self.post.id}/post_likes'
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.url}/{post_like.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

    def test_should_denied_delete401(self):
        """삭제-인증 필요"""
        post_like = baker.make('likes.PostLike', owner=self.profile, post=self.post)
        self.url = f'/api/posts/{self.post.id}/post_likes'
        response = self.client.delete(f'{self.url}/{post_like.id}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)


class PostLikeListTestCase(APITestCase):
    """게시글 좋아요 리스트 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user)
        self.post = baker.make('posts.Post')
        self.likes_count = 3
        self.post_likes = baker.make('likes.PostLike', post=self.post, _quantity=self.likes_count)
        self.url = f'/api/posts/{self.post.id}/post_likes'

    def test_should_create(self):
        """리스트-성공"""
        response = self.client.get(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        for like in res['results']:
            self.assertIsNotNone(like.get('id'))
            self.assertIsNotNone(like.get('post_id'))
            self.assertIsNotNone(like.get('owner_id'))
            owner = like['owner']
            self.assertIsNotNone(owner.get('id'))
            self.assertIsNotNone(owner.get('nickname'))
            self.assertIsNotNone(owner.get('introduce'))
            self.assertIsNone(owner['img'])


class PostListTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.profile = baker.make('users.Profile', user=self.user, nickname='test_user')
        self.post = baker.make('posts.Post')
        self.likes_count = 3
        self.post_likes = baker.make('likes.PostLike', post=self.post, _quantity=self.likes_count)
        self.url = f'/api/posts/{self.post.id}/post_likes'
