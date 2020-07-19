import datetime
import io

from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image

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
        users = baker.make('users.User', _quantity=2)
        for user in users:
            baker.make('users.Profile', user=user)
        self.url = '/api/story'
        self.user = users[0]
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
        story = baker.make('story.Story', owner=self.user, duration=datetime.timedelta(seconds=self.duration_sec))
        self.client.force_authenticate(user=self.user)

        self.assertFalse(StoryCheck.objects.filter(user=self.user, story_id=story.id).exists())
        response = self.client.get(f'{self.url}/{story.id}')
        res = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.assertEqual(res['id'], story.id)
        self.assertEqual(res['_duration'], story.duration.seconds)
        self.assertEqual(res['content'], story.content)
        self.assertTrue('img' in res)
        self.assertTrue(StoryCheck.objects.filter(user=self.user, story_id=res['id']).exists())


class StoryListTestCase(APITestCase):
    """스토리 리스트"""

    def setUp(self) -> None:
        users = baker.make('users.User', _quantity=2)
        for user in users:
            baker.make('users.Profile', user=user)
        self.url = '/api/story'
        self.user = users[0]

    def test_should_list(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        duration = 5.0
        content = 'We can do it!'
        stories = baker.make('story.Story', owner=self.user, content=content,
                             duration=datetime.timedelta(seconds=duration), _quantity=2)

        # TODO 팔로우 하는 사용자의 스토리만 리스트 필요
        for story in res['results']:
            self.assertEqual(res['_duration'], duration)
            self.assertEqual(res['content'], content)
            self.assertTrue('img' in res)
            self.assertTrue(StoryCheck.objects.filter(user=self.user, story_id=res['id']).exists())
