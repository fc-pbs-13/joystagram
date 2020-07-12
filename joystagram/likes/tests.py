from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase


class PostLikeCreateTestCase(APITestCase):
    """게시글 좋아요 생성 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.profile = baker.make('users.Profile', user=self.user, nickname='test_user')
        self.post = baker.make('posts.Post')
        self.url = f'/api/posts/{self.post.id}/post_likes'

    def test_should_create(self):
        """생성 성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)

    def test_should_duplicate(self):
        """중복 차단"""
        baker.make('likes.PostLike', owner=self.profile, post=self.post)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, res)

    def test_should_denied401(self):
        """인증 필요"""
        response = self.client.post(self.url)
        self.assertEqual(401, response.status_code, response.data)
