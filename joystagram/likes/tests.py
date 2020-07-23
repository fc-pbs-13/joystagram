from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from likes.models import PostLike
from users.models import Profile, User

INVALID_ID = -1


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
        response = self.client.post(f'/api/posts/{INVALID_ID}/likes')
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
    """좋아요 리스트"""

    def setUp(self) -> None:
        users = baker.make('users.User', _quantity=4)
        posts = []
        for user in users:
            baker.make('users.Profile', user=user, _create_files=True)
            posts.append(baker.make('posts.Post', owner=user))

        self.user = users[0]
        self.post = posts[0]
        baker.make('likes.PostLike', post=self.post, owner=self.user)
        baker.make('likes.PostLike', post=posts[1], owner=self.user)
        baker.make('likes.PostLike', post=posts[2], owner=self.user)

        baker.make('likes.PostLike', post=self.post, owner=users[1])
        baker.make('likes.PostLike', post=posts[1], owner=users[1])

    def test_post_liked_user_list(self):
        """게시글을 좋아요한 유저 리스트"""
        url = f'/api/posts/{self.post.id}/likes'
        response = self.client.get(url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        like_list = PostLike.objects.filter(post=self.post).order_by('-id')

        self.assertEqual(len(res['results']), len(like_list))

        for like_res, like_obj in zip(res['results'], like_list):
            self.assertEqual(like_res['id'], like_obj.id)
            self.assertEqual(like_res['id'], like_obj.id)

            owner = like_res['owner']
            self.assertEqual(owner['id'], like_obj.owner.id)
            self.assertEqual(owner['nickname'], like_obj.owner.profile.nickname)
            self.assertTrue('img' in owner)
            self.assertEqual(PostLike.objects.get(id=like_res['id']).post, self.post)

    def test_user_liked_post_list(self):
        """유저가 좋아요한 게시글 리스트"""
        url = f'/api/users/{self.user.id}/likes'
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        like_list = PostLike.objects.filter(owner=self.user).order_by('-id')
        self.assertEqual(len(res['results']), len(like_list))

        for like_res, like_obj in zip(res['results'], like_list):
            self.assertEqual(like_res['id'], like_obj.id)

            post = like_res['post']
            self.assertEqual(post['id'], like_obj.post.id)
            self.assertEqual(post['content'], like_obj.post.content)

            owner = post['owner']
            self.assertEqual(owner['id'], like_obj.post.owner_id)
            self.assertEqual(owner['nickname'], like_obj.post.owner.profile.nickname)
            self.assertEqual(owner['introduce'], like_obj.post.owner.profile.introduce)
            self.assertTrue('img' in owner)

            self.assertEqual(PostLike.objects.get(id=like_res['id']).owner, self.user)
