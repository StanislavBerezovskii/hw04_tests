from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTests(TestCase):
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
            text='Тестовый пост',
        )

    def test_post_model_has_correct_object_name(self):
        """Проверяем, что у модели корректно работает __str__."""
        self.assertEqual(self.post.__str__(), 'Тестовый пост')

    def test_post_model_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        post_field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in post_field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_post_model_help_texts(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        post_field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Укажите группу для поста'
        }
        for field, expected_value in post_field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTests(TestCase):
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
            text='Тестовый пост',
        )

    def test_group_model_has_correct_object_name(self):
        """Проверяем, что у модели корректно работает __str__."""
        self.assertEqual(self.group.__str__(), 'Тестовая группа')

    def test_group_model_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = self.group
        group_field_verboses = {
            'title': 'Название',
            'slug': 'URL-Адрес',
            'description': 'Описание',
        }
        for field, expected_value in group_field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_group_model_help_texts(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.group
        group_field_help_texts = {
            'title': 'Введите название группы',
            'slug': 'Введите URL-адрес группы',
            'description': 'Введите описание группы',
        }
        for field, expected_value in group_field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
