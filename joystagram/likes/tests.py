from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from likes.models import PostLike
from users.models import Profile, User


class PostLikeTestCase(APITestCase):
    """게시글 좋아요 생성, 삭제 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        self.profile = baker.make('users.Profile', user=self.user, nickname='test_user')
        self.post = baker.make('posts.Post')
        self.url = f'/api/posts/{self.post.id}/likes'

    def test_should_create(self):
        """생성-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)

    def test_should_denied_duplicate_likes(self):
        """생성-중복 차단"""
        baker.make('likes.PostLike', owner=self.user, post=self.post)
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
        response = self.client.post(f'/api/posts/{self.post.id + 1}/likes')
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, res)

    def test_should_delete(self):
        """삭제-성공"""
        post_like = baker.make('likes.PostLike', owner=self.user, post=self.post)
        self.url = f'/api/posts/{self.post.id}/likes'
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'{self.url}/{post_like.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, response.data)

    def test_should_denied_delete401(self):
        """삭제-인증 필요"""
        post_like = baker.make('likes.PostLike', owner=self.user, post=self.post)
        self.url = f'/api/posts/{self.post.id}/likes'
        response = self.client.delete(f'{self.url}/{post_like.id}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)


class PostLikedUsersListTestCase(APITestCase):
    """게시글을 좋아요한 유저 리스트"""

    def setUp(self) -> None:
        users = baker.make('users.User', _quantity=3)
        for user in users:
            baker.make('users.Profile', user=user)
        posts = baker.make('posts.Post', _quantity=3)

        baker.make('likes.PostLike', post=posts[0], owner=users[0])
        baker.make('likes.PostLike', post=posts[0], owner=users[1])
        baker.make('likes.PostLike', post=posts[1], owner=users[1])
        self.user = users[0]
        self.post = posts[0]

    def test_post_liked_people_list(self):
        """게시글을 좋아요한 유저 리스트"""
        url = f'/api/posts/{self.post.id}/likes'
        response = self.client.get(url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)

        for like in res['results']:
            self.assertTrue('id' in like)
            owner = like['owner']
            self.assertTrue('id' in owner)
            self.assertTrue('img' in owner)
            self.assertTrue('nickname' in owner)
            self.assertTrue(PostLike.objects.filter(post_id=self.post.id, owner_id=owner['id']).exists())

    def test_my_like_post_list(self):
        """유저가 좋아요한 게시글 리스트"""
        url = f'/api/users/{self.user.id}/likes'
        response = self.client.get(url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        for like in res['results']:
            self.assertIsNotNone(like.get('id'))
            post = like['post']
            self.assertTrue('id' in post)
            self.assertTrue('content' in post)
            self.assertTrue('likes_count' in post)
            self.assertTrue('like_id' in post)
            self.assertTrue(PostLike.objects.filter(post_id=post['id'], owner_id=self.user.id).exists())
