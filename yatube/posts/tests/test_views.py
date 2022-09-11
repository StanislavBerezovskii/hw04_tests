from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings as s

import math as m

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': f'{cls.group.slug}'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': f'{cls.user.username}'}):
            'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{cls.post.id}'}):
            'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{cls.post.id}'}):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def _get_first_object_(self, response):
        first_object = response.context.get('page_obj').object_list[0]
        first_object_fields = {
            first_object.text: self.post.text,
            first_object.author: self.user,
            first_object.group: self.group,
        }
        return first_object_fields

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        for item, expected in self._get_first_object_(response).items():
            with self.subTest(item=item):
                self.assertEqual(item, expected)

    def test_group_list_page_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        for item, expected in self._get_first_object_(response).items():
            with self.subTest(item=item):
                self.assertEqual(item, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))

        for item, expected in self._get_first_object_(response).items():
            with self.subTest(item=item):
                self.assertEqual(item, expected)
        page_context = {
            'username': self.user.username,
            'post_count': self.user.posts.count(),
            'post_author': self.post.author,
        }
        for item, expected in page_context.items():
            with self.subTest(item=item):
                self.assertEqual(response.context.get(f'{item}'), expected)

    def test_post_detail_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}))
        page_context = {
            'this_post': self.post,
            'author_post_count': self.post.author.posts.count(),
        }
        for item, expected in page_context.items():
            with self.subTest(item=item):
                self.assertEqual(response.context.get(f'{item}'), expected)

    def test_create_post_shows_correct_context(self):
        """Ф-я post_create передаёт в шаблон create_post верный контекст."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context.get('is_edit'), False)

    def test_post_edit_shows_correct_context(self):
        """Ф-я post_edit передаёт в шаблон create_post верный контекст."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}))
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context.get('is_edit'), True)
        self.assertEqual(response.context.get('post'), self.post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса task/test-slug/
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        for i in range(1, 17):
            cls.posts = Post.objects.bulk_create(
                [Post(text=f'Тестовый текст {i}',
                 author=cls.user,
                 group=cls.group)])
        cls.page_count = m.ceil(len(cls.posts) / 10)

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Тест паджинатора. На первой странице не более 10 объектов."""
        response = self.client.get(reverse('posts:index'))
        self.assertLessEqual(len(response.context.get('page_obj')), s.PER_PAGE)

    def test_second_page_contains_three_records(self):
        """Тест паджинатора. На второй и последующих
        страницах не более 10 объектов."""
        for i in range(2, self.page_count):
            response = self.client.get(reverse('posts:index') + f'?page={i}')
            self.assertLessEqual(
                len(response.context.get('page_obj')), s.PER_PAGE)
