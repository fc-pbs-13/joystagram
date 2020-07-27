from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from relationships.models import Follow
from users.models import User


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
        baker.make('relationships.Follow', owner=self.user, to_user=self.to_user)
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
        follow = baker.make('relationships.Follow', owner=self.user, to_user=self.to_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/follows/{follow.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

    def test_should_denied_delete401(self):
        """삭제-인증 필요"""
        follow = baker.make('relationships.Follow', owner=self.user, to_user=self.to_user)
        response = self.client.delete(f'/api/follows/{follow.id}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)


class FollowListTestCase(APITestCase):
    """팔로우 리스트 테스트"""

    def setUp(self) -> None:
        users = baker.make('users.User', _quantity=4)
        for user in users:
            baker.make('users.Profile', user=user)

        self.user = users[0]
        baker.make('relationships.Follow', owner=self.user, to_user=users[1])
        baker.make('relationships.Follow', owner=self.user, to_user=users[2])

        baker.make('relationships.Follow', owner=users[1], to_user=self.user)
        baker.make('relationships.Follow', owner=users[2], to_user=self.user)
        baker.make('relationships.Follow', owner=users[3], to_user=self.user)

        baker.make('relationships.Follow', owner=users[1], to_user=users[2])
        self.client.force_authenticate(user=self.user)

    def test_should_list_follower(self):
        """유저를 팔로잉하는 유저 리스트"""
        response = self.client.get(f'/api/users/{self.user.id}/followers')
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)

        user_list = User.objects.filter(
            id__in=Follow.objects.filter(to_user_id=self.user).values('owner_id')
        ).select_related('profile').order_by('-id')
        self.assertEqual(len(user_list), len(Follow.objects.filter(to_user_id=self.user)))

        self.assertEqual(len(res['results']), user_list.count())
        for user_res, user_obj in zip(res['results'], user_list):
            self.follow_test(user_res, user_obj, True)

    def test_should_list_following(self):
        """유저가 팔로우한 유저 리스트"""
        response = self.client.get(f'/api/users/{self.user.id}/followings')
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)

        user_list = User.objects.filter(
            id__in=Follow.objects.filter(owner_id=self.user).values('to_user_id')
        ).select_related('profile').order_by('-id')
        self.assertEqual(len(user_list), len(Follow.objects.filter(owner_id=self.user)))

        self.assertEqual(len(res['results']), user_list.count())
        for user_res, user_obj in zip(res['results'], user_list):
            self.follow_test(user_res, user_obj, False)

    def follow_test(self, user_res, user_obj, is_follower):
        self.assertEqual(user_res['id'], user_obj.id)
        self.assertTrue('img' in user_res)
        self.assertEqual(user_res['nickname'], user_obj.profile.nickname)
        self.assertEqual(user_res['introduce'], user_obj.profile.introduce)

        if user_res['follow_id']:
            self.assertTrue(Follow.objects.filter(id=user_res['follow_id'],
                                                  owner=self.user,
                                                  to_user_id=user_res['id']).exists())
        if is_follower:
            self.assertTrue(Follow.objects.filter(owner=user_res['id'], to_user_id=self.user).exists())
