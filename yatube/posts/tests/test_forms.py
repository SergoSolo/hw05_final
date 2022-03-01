import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='serg')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Любой текст',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = PostCreateFormTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый пост',
            'group': PostCreateFormTests.post.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={
                    'username': PostCreateFormTests.user
                }
            )
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        latest_post = Post.objects.latest('id')
        self.assertTrue(
            Post.objects.filter(
                id=latest_post.id,
                text=form_data['text'],
                group=form_data['group'],
                image=latest_post.image
            ).exists()
        )

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированно!',
            'group': PostCreateFormTests.post.group.id
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={
                    'post_id': PostCreateFormTests.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostCreateFormTests.post.id
                }
            )
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                id=PostCreateFormTests.post.id,
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )

    def test_create_comment(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Коммент'
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={
                    'post_id': PostCreateFormTests.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostCreateFormTests.post.id
                }
            )
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        latest_comment = Comment.objects.latest('id')
        self.assertTrue(
            Comment.objects.filter(
                id=latest_comment.id,
                text=form_data['text'],
            ).exists()
        )
