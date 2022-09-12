from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings as s

import math

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
        cls.index_reverse = reverse('posts:index')
        cls.group_reverse = reverse('posts:group_list',
                                    kwargs={'slug': f'{cls.group.slug}'})
        cls.profile_reverse = reverse('posts:profile',
                                      kwargs={'username':
                                              f'{cls.user.username}'})
        cls.post_reverse = reverse('posts:post_detail',
                                   kwargs={'post_id': f'{cls.post.id}'})
        cls.edit_reverse = reverse('posts:post_edit',
                                   kwargs={'post_id': f'{cls.post.id}'})
        cls.create_reverse = reverse('posts:post_create')
        cls.reverse_list = [cls.index_reverse,
                            cls.group_reverse,
                            cls.profile_reverse,
                            cls.post_reverse,
                            cls.edit_reverse,
                            cls.create_reverse]
        cls.templates_list = ['posts/index.html',
                              'posts/group_list.html',
                              'posts/profile.html',
                              'posts/post_detail.html',
                              'posts/create_post.html',
                              'posts/create_post.html']

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
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
        reverse_template_dict = dict(zip(self.reverse_list,
                                     self.templates_list))
        for reverse_name, template in reverse_template_dict.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.index_reverse)
        for item, expected in self._get_first_object_(response).items():
            with self.subTest(item=item):
                self.assertEqual(item, expected)

    def test_group_list_page_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.group_reverse)
        for item, expected in self._get_first_object_(response).items():
            with self.subTest(item=item):
                self.assertEqual(item, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.profile_reverse)
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
        response = self.authorized_client.get(self.post_reverse)
        page_context = {
            'this_post': self.post,
            'author_post_count': self.post.author.posts.count(),
        }
        for item, expected in page_context.items():
            with self.subTest(item=item):
                self.assertEqual(response.context.get(f'{item}'), expected)

    def test_create_post_shows_correct_context(self):
        """Ф-я post_create передаёт в шаблон create_post верный контекст."""
        response = self.authorized_client.get(self.create_reverse)
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context.get('is_edit'), False)

    def test_post_edit_shows_correct_context(self):
        """Ф-я post_edit передаёт в шаблон create_post верный контекст."""
        response = self.authorized_client.get(self.edit_reverse)
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertEqual(response.context.get('is_edit'), True)
        self.assertEqual(response.context.get('post'), self.post)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.test_posts = []
        for i in range(23):
            cls.test_posts.append(Post(
                text=f'Тестовый пост №{i}',
                group=cls.group,
                author=cls.user))
        Post.objects.bulk_create(cls.test_posts)
        # Я мог бы взять здесь //, но math.ceil() очень просто округляет сразу
        cls.page_count = math.ceil(len(cls.test_posts) / s.PER_PAGE)

    def setUp(self):
        self.guest_client = Client()

    def test_page_elements_number(self):
        if len(self.test_posts) <= 10:
            response = self.client.get(reverse('posts:index'))
            self.assertLessEqual(len(response.context.get('page_obj')),
                                 len(self.test_posts))
        else:
            response = self.client.get(reverse('posts:index'))
            self.assertLessEqual(len(response.context.get('page_obj')),
                                 s.PER_PAGE)
            for i in range(2, self.page_count - 1):
                response = self.client.get(
                    reverse('posts:index') + f'?page={i}')
                self.assertEqual(
                    len(response.context.get('page_obj')), s.PER_PAGE)
            for i in range(self.page_count, self.page_count):
                response = self.client.get(
                    reverse('posts:index') + f'?page={i}')
                self.assertEqual(
                    len(response.context.get('page_obj')),
                    len(self.test_posts) % s.PER_PAGE)
