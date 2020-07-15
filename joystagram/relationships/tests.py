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
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

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


class FollowListTestCase(APITestCase):
    """팔로우 리스트 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user)
        self.follow_count = 3
        users = baker.make('users.User', _quantity=self.follow_count)
        for user in users:
            baker.make('users.Profile', user=user)
            baker.make('relationships.Follow', from_user=self.user, to_user=user)
        self.url = f'/api/follows'

    def test_should_list(self):
        """리스트-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        for follow in res['results']:
            self.assertIsNotNone(follow.get('id'))
            to_user = follow['user']
            self.assertTrue('id' in to_user)
            self.assertTrue('nickname' in to_user)
            self.assertTrue('img' in to_user)
