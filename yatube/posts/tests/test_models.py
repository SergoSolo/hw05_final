from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Любой текст',
        )

    def test_models_have_correct_object_names(self):
        post = PostModelTest.post
        expected_post = post.text[:15]
        self.assertEqual(expected_post, str(post))

    def test_model_group_have_correct_name(self):
        group = PostModelTest.group
        self.assertEqual(group.title, str(group))

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
        }
        for field, expected_values in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_values
                )

    def test_help_text(self):
        post = PostModelTest.post
        field_help_text = {
            'text': 'Напишите что угодно!',
            'group': 'Можете выбрать группу или оставить так.',
        }
        for field, expected_values in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_values
                )
