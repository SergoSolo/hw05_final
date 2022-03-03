from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post
from ..utils import assertequal_test

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='serg')
        cls.not_sub_user = User.objects.create_user(username='not_sub')
        cls.sub_user = User.objects.create_user(username='sub')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Любой текст',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Любой текст',
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_sub = Client()
        self.authorized_client_sub.force_login(self.sub_user)
        self.authorized_client_not_sub = Client()
        self.authorized_client_not_sub.force_login(self.not_sub_user)
        self.group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Любой текст 2',
            group=self.group,
            image=self.uploaded
        )
        self.follow = Follow.objects.create(
            user=self.sub_user,
            author=self.user
        )

    def test_uses_correct_template(self):
        views_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostViewsTest.post.group.slug
                }
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={
                    'username': PostViewsTest.user
                }
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostViewsTest.post.id
                }
            ): 'posts/post_detail.html',
            reverse('posts:create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': PostViewsTest.post.id
                }
            ): 'posts/create_post.html'
        }
        for address, template in views_template.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_context_homepage_group_profile(self):
        context_template = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.group.slug
                }
            ): 'page_obj',
            reverse(
                'posts:profile', kwargs={
                    'username': self.user
                }
            ): 'page_obj',
        }
        for page, page_obj in context_template.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                first_obj = response.context[page_obj][0]
                assertequal_test(self, first_obj, self.post)

    def test_context_post_detail(self):
        response = self.client.get(
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostViewsTest.post.id
                }
            )
        )
        post_obj = response.context['post']
        assertequal_test(self, post_obj, PostViewsTest.post)

    def test_post_in_correct_pages(self):
        post_template = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostViewsTest.post.group.slug
                }
            ): 'page_obj',
            reverse(
                'posts:profile', kwargs={'username': PostViewsTest.user}
            ): 'page_obj',
        }
        for adress, page_obj in post_template.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                posts_list = response.context.get(page_obj).object_list
                self.assertIn(PostViewsTest.post, posts_list)

    def test_post_not_in_correct_group(self):
        response = self.client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostViewsTest.group.slug
                }
            )
        )
        posts_list = response.context.get('page_obj')
        self.assertNotIn(self.post, posts_list)

    def test_comment_in_correct_page(self):
        response = self.client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': PostViewsTest.post.id}
            )
        )
        comments_list = response.context['comments']
        self.assertIn(PostViewsTest.comment, comments_list)

    def test_posts_context_in_favorits_page(self):
        response = self.authorized_client_sub.get(
            reverse('posts:follow_index')
        )
        first_obj = response.context['page_obj'][0]
        assertequal_test(self, first_obj, self.post)

    def test_posts_in_favorits_page(self):
        response = self.authorized_client_sub.get(
            reverse('posts:follow_index')
        )
        posts = response.context.get('page_obj').object_list
        self.assertIn(self.post, posts)

    def test_posts_not_in_favorits_page(self):
        response = self.authorized_client.get(reverse('posts:follow_index'))
        posts = response.context.get('page_obj').object_list
        self.assertNotIn(self.post, posts)

    def test_follow(self):
        self.authorized_client_not_sub.get(
            reverse(
                'posts:profile_follow', kwargs={
                    'username': PostViewsTest.user
                }
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.not_sub_user,
                author=PostViewsTest.user
            ).exists()
        )

    def test_unfollow(self):
        Follow.objects.create(
            user=self.not_sub_user,
            author=PostViewsTest.user
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.not_sub_user,
                author=PostViewsTest.user
            ).exists())
        self.authorized_client_not_sub.get(
            reverse(
                'posts:profile_unfollow', kwargs={
                    'username': PostViewsTest.user
                }
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.not_sub_user,
                author=PostViewsTest.user
            ).exists()
        )

    def test_view_form_create(self):
        response = self.authorized_client.get(reverse('posts:create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_view_form_edit(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': PostViewsTest.post.id
                }
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        first_response = self.client.get(reverse('posts:index'))
        first_content = first_response.content
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тест кэш',
        }
        self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        second_response = self.client.get(reverse('posts:index'))
        second_content = second_response.content
        self.assertEqual(first_content, second_content)
        cache.clear()
        third_response = self.client.get(reverse('posts:index'))
        third_content = third_response.content
        self.assertNotEqual(second_content, third_content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='serg')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        num = settings.POSTS_NUM + 3
        cls.post = Post.objects.bulk_create(
            [Post(
                author=cls.user,
                text='Любойтекст %s' % post,
                group=cls.group)
                for post in range(num)]
        )

    def setUp(self):
        cache.clear()
        self.user = PaginatorViewsTest.user

    def test_pagination(self):
        paginator_template = {
            reverse('posts:index'): 'page_obj',
            reverse(
                'posts:group_list', kwargs={
                    'slug': PaginatorViewsTest.group.slug
                }
            ): 'page_obj',
            reverse(
                'posts:profile', kwargs={
                    'username': PaginatorViewsTest.user
                }
            ): 'page_obj'
        }
        for address, value in paginator_template.items():
            with self.subTest(value=value):
                response = self.client.get(address)
                response_second = self.client.get(address + '?page=2')
                self.assertEqual(
                    len(response.context[value]), settings.POSTS_NUM
                )
                diff_count = Post.objects.count() - settings.POSTS_NUM
                if diff_count > settings.POSTS_NUM:
                    self.assertEqual(
                        len(response_second.context[value]), settings.POSTS_NUM
                    )
                else:
                    self.assertEqual(len(
                        response_second.context[value]), diff_count
                    )
