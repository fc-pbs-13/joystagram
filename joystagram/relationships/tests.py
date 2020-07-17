from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from relationships.models import Follow


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
        users = baker.make('users.User', _quantity=4)
        for user in users:
            baker.make('users.Profile', user=user)

        baker.make('relationships.Follow', from_user=users[0], to_user=users[1])
        baker.make('relationships.Follow', from_user=users[0], to_user=users[2])
        baker.make('relationships.Follow', from_user=users[1], to_user=users[2])
        baker.make('relationships.Follow', from_user=users[1], to_user=users[0])
        baker.make('relationships.Follow', from_user=users[2], to_user=users[0])
        self.user = users[1]

    def test_should_list_following(self):
        """유저가 팔로우한 유저 리스트"""
        response = self.client.get(f'/api/users/{self.user.id}/followings')
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.assertEqual(len(res['results']), Follow.objects.filter(from_user=self.user).count())

        for follow in res['results']:
            self.assertTrue('id' in follow)
            user = follow['user']
            self.assertTrue('id' in user)
            self.assertTrue('img' in user)
            self.assertTrue('nickname' in user)
            self.assertTrue(Follow.objects.filter(from_user=self.user, to_user_id=user['id']).exists())

    def test_should_list_follower(self):
        """유저를 팔로잉하는 유저 리스트"""
        response = self.client.get(f'/api/users/{self.user.id}/followers')
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.assertEqual(len(res['results']), Follow.objects.filter(to_user=self.user).count())

        for follow in res['results']:
            self.assertTrue('id' in follow)
            user = follow['user']
            self.assertTrue('id' in user)
            self.assertTrue('img' in user)
            self.assertTrue('nickname' in user)
            self.assertTrue(Follow.objects.filter(from_user=self.user, to_user_id=user['id']).exists())
