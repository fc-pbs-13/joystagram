from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase
from comments.models import Comment, ReComment

INVALID_ID = -1


class CommentCreateTestCase(APITestCase):
    """댓글 생성 테스트"""

    def setUp(self) -> None:
        self.data = {
            'content': 'hello joy This is Comment!!'
        }
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user)
        self.post = baker.make('posts.Post', owner=self.user)
        self.url = f'/api/posts/{self.post.id}/comments'

    def test_should_create(self):
        """생성-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=self.data)
        res = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, res)
        self.assertEqual(res['content'], self.data['content'])

        owner = res.get('owner')
        self.assertIsNotNone(owner)
        self.assertIsNotNone(owner.get('id'))
        self.assertIsNotNone(owner.get('nickname'))

        recomments = res.get('recomments')
        self.assertIsNotNone(recomments)
        for recomment in recomments:
            self.assertIsNotNone(recomment)
            self.assertIsNotNone(recomment.get())
        self.assertTrue(Comment.objects.filter(id=res.get('id')).exists())

    def test_should_denied(self):
        """생성-인증 필요"""
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_denied_invalid_id(self):
        """생성-유효하지 않은 post_id"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/posts/{INVALID_ID}/comments', data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentListTestCase(APITestCase):
    """댓글 리스트 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user)
        self.post = baker.make('posts.Post')
        self.comment_size = 3
        self.comments = baker.make('comments.Comment', post=self.post, owner=self.user, _quantity=self.comment_size)
        baker.make('comments.Comment')
        self.url = f'/api/posts/{self.post.id}/comments'

    def test_should_list(self):
        """리스트-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(len(response.data), self.comment_size)

        for comment_res, comment_obj in zip(response.data['results'],
                                            Comment.objects.filter(post=self.post).order_by('-id')):
            self.assertEqual(comment_res['id'], comment_obj.id)
            self.assertEqual(comment_res['content'], comment_obj.content)
            owner = comment_res['owner']
            self.assertEqual(owner['id'], comment_obj.owner.id)
            self.assertEqual(owner['nickname'], comment_obj.owner.profile.nickname)
            self.assertEqual(comment_res['recomments_count'], comment_obj.recomments.count())
            self.assertEqual(Comment.objects.get(id=comment_res['id']).post, self.post)


class CommentUpdateDeleteTestCase(APITestCase):
    """댓글 수정, 삭제 테스트"""

    def setUp(self) -> None:
        self.data = {'content': 'update_comment'}
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user)
        comment = baker.make('comments.Comment', owner=self.user)
        self.url = f'/api/comments/{comment.id}'

    def test_should_update(self):
        """수정-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data=self.data)
        res = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK, res)
        self.assertEqual(res['content'], self.data['content'])

    def test_should_denied_update401(self):
        """수정-필요"""
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_denied_update403(self):
        """수정-권한 없음"""
        invalid_user = baker.make('users.User')
        baker.make('users.Profile', user=invalid_user)
        self.client.force_authenticate(user=invalid_user)
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_delete(self):
        """삭제-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        res = response.data
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, res)

    def test_should_denied_delete401(self):
        """삭제-인증 필요"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_denied_delete403(self):
        """삭제-권한 없음"""
        invalid_user = baker.make('users.User')
        baker.make('users.Profile', user=invalid_user)
        self.client.force_authenticate(user=invalid_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ReCommentCreateTestCase(APITestCase):
    """대댓글 생성 테스트"""

    def setUp(self):
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user, nickname='test_user')
        self.comment = baker.make('comments.Comment')
        self.url = f'/api/comments/{self.comment.id}/recomments'
        self.data = {"content": "blah"}

    def test_should_create(self):
        """생성-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        res = response.data
        self.assertIsNotNone(res['id'])
        self.assertIsNotNone(res['content'])
        self.assertIsNotNone(res['owner'])

    def test_should_denied_create401(self):
        """생성-인증 필요"""
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_denied_invalid_id(self):
        """생성-유효하지 않은 comment_id"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/comments/{INVALID_ID}/recomments', data=self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ReCommentListTestCase(APITestCase):
    """대댓글 리스트 테스트"""

    def setUp(self) -> None:
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user)
        self.comment = baker.make('comments.Comment', owner=self.user)
        baker.make('comments.ReComment', comment=self.comment, owner=self.user, _quantity=3)
        baker.make('comments.ReComment', _quantity=2)
        self.url = f'/api/comments/{self.comment.id}/recomments'

    def test_should_list(self):
        """리스트-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        res = response.data
        for recomment in res['results']:
            self.assertIsNotNone(recomment['id'])
            self.assertIsNotNone(recomment['content'])
            self.assertIsNotNone(recomment['owner'])
            self.assertEqual(ReComment.objects.get(id=recomment['id']).comment, self.comment)

        for recomment_res, recomment_obj in zip(response.data['results'],
                                                ReComment.objects.filter(comment=self.comment).order_by('-id')):
            self.assertEqual(recomment_res['id'], recomment_obj.id)
            self.assertEqual(recomment_res['content'], recomment_obj.content)
            owner = recomment_res['owner']
            self.assertEqual(owner['id'], recomment_obj.owner.id)
            self.assertEqual(owner['nickname'], recomment_obj.owner.profile.nickname)
            self.assertEqual(ReComment.objects.get(id=recomment_res['id']).comment, self.comment)


class ReCommentUpdateDeleteTestCase(APITestCase):
    """대댓글 수정, 삭제 테스트"""

    def setUp(self) -> None:
        self.data = {'content': 'update_recomment'}
        self.user = baker.make('users.User')
        baker.make('users.Profile', user=self.user)
        recomment = baker.make('comments.ReComment', owner=self.user)
        self.url = f'/api/recomments/{recomment.id}'

    def test_should_update(self):
        """수정-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data=self.data)
        res = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res['content'], self.data['content'])

    def test_should_denied_update401(self):
        """수정-인증 필요"""
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_denied_update403(self):
        """수정-권한 없음"""
        invalid_user = baker.make('users.User')
        baker.make('users.Profile', user=invalid_user)
        self.client.force_authenticate(user=invalid_user)
        response = self.client.patch(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_should_delete(self):
        """삭제-성공"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_should_denied_delete401(self):
        """삭제-인증 필요"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_should_denied_delete403(self):
        """삭제-권한 없음"""
        invalid_user = baker.make('users.User')
        baker.make('users.Profile', user=invalid_user)
        self.client.force_authenticate(user=invalid_user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
