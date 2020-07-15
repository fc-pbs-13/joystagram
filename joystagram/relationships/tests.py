from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from likes.models import PostLike
from users.models import Profile


class FollowTestCase(APITestCase):
    """팔로우 생성, 삭제 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.to_user = baker.make('users.User')
        baker.make('users.Profile', user=self.user)
        baker.make('users.Profile', user=self.to_user)
        self.url = f'/api/users/{self.to_user.id}/follows'

    def test_should_create(self):
        """생성-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)

    def test_should_denied_duplicate_likes(self):
        """생성-중복 차단"""
        baker.make('relationships.Follow', from_user=self.user, to_user=self.to_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_should_denied_create_401(self):
        """생성-인증 필요"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_should_denied_invalid_post_id(self):
        """생성-유효하지 않은 post_id"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/users/{self.to_user.id + 1}/follows')
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, res)

    def test_should_delete(self):
        """삭제-성공"""
        follow = baker.make('relationships.Follow', from_user=self.user, to_user=self.to_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/follows/{follow.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

    def test_should_denied_delete401(self):
        """삭제-인증 필요"""
        follow = baker.make('relationships.Follow', from_user=self.user, to_user=self.to_user)
        response = self.client.delete(f'/api/follows/{follow.id}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

#
# class PostLikeListTestCase(APITestCase):
#     """게시글 좋아요 리스트 테스트"""
#
#     def setUp(self) -> None:
#         self.user = baker.make('users.User')
#         baker.make('users.Profile', user=self.user)
#         self.post = baker.make('posts.Post')
#         self.likes_count = 2
#         users = baker.make('users.User', _quantity=self.likes_count)
#         for user in users:
#             baker.make('users.Profile', user=user)
#             self.post_likes = baker.make('likes.PostLike', post=self.post, owner=user)
#         self.url = f'/api/posts/{self.post.id}/post_likes'
#
#     def test_should_create(self):
#         """리스트-성공"""
#         response = self.client.get(self.url)
#         res = response.data
#         self.assertEqual(response.status_code, status.HTTP_200_OK, res)
#         for like in res['results']:
#             self.assertIsNotNone(like.get('id'))
#             self.assertIsNotNone(like.get('post_id'))
#             self.assertIsNotNone(like.get('owner_id'))
#             owner = like['owner']
#             self.assertIsNotNone(owner.get('id'))
#             self.assertIsNotNone(owner.get('nickname'))
#             self.assertIsNone(owner.get('introduce'))  # introduce 빼고
#             self.assertTrue('img' in owner)
