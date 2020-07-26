from datetime import timedelta, datetime

import pytz
from django.db.models import Q
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from core.tests import TempFileMixin
from relationships.models import Follow
from story.models import StoryCheck, Story

INVALID_ID = -1


class StoryTestCase(APITestCase, TempFileMixin):
    """스토리 생성, 삭제 테스트"""

    def setUp(self) -> None:
        self.users = baker.make('users.User', _quantity=3)
        for user in self.users:
            baker.make('users.Profile', user=user)
        self.url = '/api/story'
        self.user = self.users[0]
        self.owner = self.users[1]
        baker.make('relationships.Follow', from_user=self.user, to_user=self.owner)

        self.duration_sec = 5.0
        self.data = {
            'content': 'dsds',
            'img': self.generate_photo_file(),
            'duration': timedelta(seconds=self.duration_sec)
        }
        self.yesterday = timezone.now() - timedelta(days=1)

    def list_setUp(self):
        self.valid_story_count = 2
        valid_created = timezone.now() - timedelta(hours=23, minutes=59)
        invalid_created1 = timezone.now() - timedelta(days=1, seconds=1)
        invalid_created2 = timezone.now() + timedelta(seconds=1)
        # valid 2 stories
        self.story = baker.make('story.Story', owner=self.owner, created=valid_created)
        baker.make('story.Story', owner=self.user, created=valid_created)
        # invalid 4 stories
        baker.make('story.Story', owner=self.owner, created=invalid_created1)
        baker.make('story.Story', owner=self.owner, created=invalid_created2)
        baker.make('story.Story', owner=self.users[2], _quantity=2, created=valid_created)

    def test_should_create(self):
        """생성-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=self.data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_should_denied_create(self):
        """생성-인증 필요"""
        response = self.client.post(self.url, data=self.data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)

    def test_should_retrieve(self):
        """스토리 조회"""
        story = baker.make('story.Story', owner=self.owner)
        self.client.force_authenticate(user=self.user)

        self.assertEqual(StoryCheck.objects.filter(user=self.owner, story_id=story.id).count(), 0)
        response = self.client.get(f'{self.url}/{story.id}')
        res = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.story_test(res, story)

        # 다시 조회: StoryCheck 갯수 하나인지 체크
        response = self.client.get(f'{self.url}/{story.id}')
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.assertEqual(res['read_users_count'], StoryCheck.objects.filter(user=self.user, story_id=res['id']).count())

    def test_retrieve_own_story(self):
        user = self.user
        story = baker.make('story.Story', owner=user)
        baker.make('story.StoryCheck', user=self.users[1], story=story)
        self.client.force_authenticate(user=user)

        self.assertEqual(StoryCheck.objects.filter(story_id=story.id).count(), 1)
        response = self.client.get(f'{self.url}/{story.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(StoryCheck.objects.filter(story_id=story.id).count(), 1)

    def list_read_users_setUp(self):
        self.client.force_authenticate(user=self.user)
        self.story = baker.make('story.Story', owner=self.owner)
        baker.make('story.StoryCheck', story=self.story, user=self.users[2])

    def test_should_list_read_users(self):
        """내 스토리를 읽은 유저 리스트"""
        self.list_read_users_setUp()
        response = self.client.get(f'{self.url}/{self.story.id}/users')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        res = response.data['results']
        self.assertEqual(len(res), 1)
        self.assertEqual(StoryCheck.objects.filter(user_id=res[0]['id'], story=self.story).count(), 1)

    def test_list_read_users_invalid_id(self):
        """내 스토리를 읽은 유저 리스트 - 유효하지 않은 story_id"""
        self.list_read_users_setUp()

        response = self.client.get(f'{self.url}/{INVALID_ID}/users')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, response.data)

    def test_should_list(self):
        """
        스토리 리스트
        내가 팔로우하는 유저의 스토리 중 등록 후 24시간이 지나지 않은 것만
        """
        self.list_setUp()  # setUp
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)

        story_list = Story.objects.filter(
            Q(owner_id__in=Follow.objects.filter(from_user=self.user).values('to_user_id')) |
            Q(owner=self.user)
        ).filter(created__gte=timezone.now() - timedelta(days=1),
                 created__lte=timezone.now()).order_by('-id')

        self.assertEqual(len(res['results']), self.valid_story_count)
        self.assertEqual(len(res['results']), len(story_list))

        for story_res, story_obj in zip(res['results'], story_list):
            self.story_test(story_res, story_obj)

            # 자신 혹은 팔로우 하는 사용자의 스토리
            owner = story_res['owner']
            self.assertTrue(
                Follow.objects.filter(from_user=self.user, to_user_id=owner['id']).exists()
                or self.user.id == owner['id']
            )
            # watched 검사
            self.assertFalse(story_res['watched'])

    def test_should_list_watched(self):
        """내가 본 스토리인지 체크"""
        self.list_setUp()  # setUp
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.url}/{self.story.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        response = self.client.get(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)

        for story_res in res['results']:
            watched = story_res['watched']
            if story_res['id'] == self.story.id:
                self.assertTrue(watched)
            else:
                self.assertFalse(watched)

    def story_test(self, story_res, story_obj):
        """스토리 필드 검사"""
        self.assertEqual(story_res['id'], story_obj.id)
        self.assertEqual(story_res['_duration'], story_obj.duration.seconds)
        self.assertEqual(story_res['content'], story_obj.content)
        self.assertTrue('img' in story_res)

        self.assertGreater(story_obj.created, timezone.now() - timedelta(days=1))
        self.assertLess(story_obj.created, timezone.now())
        # 등록시간 24시간 검사
        created_res = pytz.utc.localize(datetime.strptime(story_res['created'], '%Y-%m-%dT%H:%M:%S.%fZ'))
        self.assertTrue(self.yesterday < created_res < timezone.now())

    def test_should_update(self):
        """수정"""
        story = baker.make('story.Story', owner=self.user)
        data = {
            'content': 'updated_content'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'{self.url}/{story.id}', data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['content'], data['content'])
        self.assertEqual(Story.objects.get(id=story.id).content, data['content'])

    def test_should_destroy(self):
        """삭제"""
        story = baker.make('story.Story', owner=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.url}/{story.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)
        self.assertFalse(Story.objects.filter(id=story.id).exists())
