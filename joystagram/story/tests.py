import datetime
import io

from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image

from relationships.models import Follow
from story.models import StoryCheck, Story


class StoryTestCase(APITestCase):
    """스토리 생성, 삭제 테스트"""

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
            'duration': datetime.timedelta(seconds=self.duration_sec)
        }

    def test_should_create(self):
        """생성-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=self.data, format='multipart')  # TODO 포맷 적용 안바꿔도 이미지 업로드 가능?
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)

    def test_should_denied_create(self):
        """생성-인증 필요"""
        response = self.client.post(self.url, data=self.data, format='multipart')
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, res)

    def test_should_retrieve(self):
        """스토리 조회"""
        story = baker.make('story.Story', owner=self.owner, duration=datetime.timedelta(seconds=self.duration_sec))
        self.client.force_authenticate(user=self.user)

        self.assertEqual(StoryCheck.objects.filter(user=self.owner, story_id=story.id).count(), 0)
        response = self.client.get(f'{self.url}/{story.id}')
        res = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.story_test(res, story)

        # 다시 조회
        response = self.client.get(f'{self.url}/{story.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.assertEqual(StoryCheck.objects.filter(user=self.user, story_id=response.data['id']).count(), 1)

    def test_should_list(self):
        """
        스토리 리스트
        내가 팔로우하는 유저의 스토리 중 등록 후 24시간이 지나지 않은 것만
        """
        baker.make('story.Story', owner=self.user, _quantity=2)
        baker.make('story.Story', owner=self.owner, _quantity=2)
        baker.make('story.Story', owner=self.users[2])
        self.url = '/api/story'

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)

        story_list = Story.objects.filter(
            owner_id__in=Follow.objects.filter(from_user=self.user).values('to_user_id')
        )

        # TODO 팔로우 하는 사용자의 스토리인지, 등록 시간이 24시간 내 인지 체크
        self.assertEqual(len(res['results']), len(story_list))
        self.assertEqual(len(res['results']), 2)
        for story_res, story_obj in zip(res['results'], story_list[::-1]):
            print(story_res)
            self.story_test(story_res, story_obj)
            owner = story_res['owner']
            self.assertTrue(Follow.objects.filter(from_user=self.user, to_user_id=owner['id']).exists())

    def story_test(self, story_res, story_obj):
        self.assertEqual(story_res['id'], story_obj.id)
        self.assertEqual(story_res['_duration'], story_obj.duration.seconds)
        self.assertEqual(story_res['content'], story_obj.content)
        self.assertTrue('img' in story_res)
