from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.not_auth = User.objects.create_user(username='not_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Любой текст',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Любой текст',
        )
        cls.follow = Follow.objects.create(
            user=cls.not_auth,
            author=cls.user
        )

    def setUp(self):
        cache.clear()
        self.user = PostUrlTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_auth = PostUrlTests.not_auth
        self.authorized_client_not_auth = Client()
        self.authorized_client_not_auth.force_login(self.not_auth)
        self.post = Post.objects.create(
            author=self.not_auth,
            text='Любой текст 2',
        )
        self.follow = Follow.objects.create(
            user=self.user,
            author=self.not_auth
        )

    def test_status_guest_client_pages(self):
        urls_template = {
            '/': HTTPStatus.OK,
            f'/group/{PostUrlTests.post.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostUrlTests.user}/': HTTPStatus.OK,
            f'/posts/{PostUrlTests.post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{PostUrlTests.post.id}/edit/': HTTPStatus.FOUND,
            '/not_exist/': HTTPStatus.NOT_FOUND,
            f'/posts/{PostUrlTests.post.id}/comment/': HTTPStatus.FOUND,
            f'/profile/{PostUrlTests.user}/follow/': HTTPStatus.FOUND,
            f'/profile/{PostUrlTests.user}/unfollow/': HTTPStatus.FOUND,
        }
        for address, status in urls_template.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, status)

    def test_redirecting_guest_client(self):
        urls_template = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{PostUrlTests.post.id}/edit/':
            f'/auth/login/?next=/posts/{PostUrlTests.post.id}/edit/',
            f'/posts/{PostUrlTests.post.id}/comment/':
            f'/auth/login/?next=/posts/{PostUrlTests.post.id}/comment/',
            '/follow/': '/auth/login/?next=/follow/',
            f'/profile/{PostUrlTests.user}/follow/':
            f'/auth/login/?next=/profile/{PostUrlTests.user}/follow/',
            f'/profile/{PostUrlTests.user}/unfollow/':
            f'/auth/login/?next=/profile/{PostUrlTests.user}/unfollow/'
        }
        for adress, template in urls_template.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertRedirects(response, template)

    def test_status_authorizd_client_page(self):
        urls_template = {
            '/create/': HTTPStatus.OK,
            f'/posts/{PostUrlTests.post.id}/edit/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
            f'/profile/{PostUrlTests.not_auth}/follow/': HTTPStatus.FOUND,
            f'/profile/{PostUrlTests.not_auth}/unfollow/': HTTPStatus.FOUND,
        }
        for address, status in urls_template.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_redirecting_not_author(self):
        urls_template = {
            f'/posts/{PostUrlTests.post.id}/edit/':
            f'/posts/{PostUrlTests.post.id}/',
            f'/profile/{PostUrlTests.user}/follow/': '/follow/',
            f'/profile/{PostUrlTests.user}/unfollow/':
            f'/profile/{PostUrlTests.user}/'
        }
        for adress, template in urls_template.items():
            with self.subTest(adress=adress):
                response = self.authorized_client_not_auth.get(adress)
                self.assertRedirects(response, template)

    def test_urls_uses_correct_template(self):
        urls_template = {
            '/': 'posts/index.html',
            f'/group/{PostUrlTests.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostUrlTests.user}/': 'posts/profile.html',
            f'/posts/{PostUrlTests.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostUrlTests.post.id}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
            '/not_exist/': 'core/404.html'
        }
        for address, template in urls_template.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
