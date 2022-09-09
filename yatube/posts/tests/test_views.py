from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

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

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'TestUser'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={
                    'post_id': f'{self.post.id}'
                })
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={
                    'post_id': f'{self.post.id}'
                })
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context.get('page_obj').object_list[0]
        first_object_fields = {
            first_object.text: self.post.text,
            first_object.author: self.user,
            first_object.group: self.group,
        }
        for item, expected in first_object_fields.items():
            with self.subTest(item=item):
                self.assertEqual(item, expected)

    def test_group_list_page_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        first_object = response.context.get('page_obj').object_list[0]
        self.assertEqual(response.context.get('group'), self.group)
        first_object_fields = {
            first_object.text: self.post.text,
            first_object.author: self.user,
            first_object.group: self.group,
        }
        for item, expected in first_object_fields.items():
            with self.subTest(item=item):
                self.assertEqual(item, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        first_object = response.context.get('page_obj').object_list[0]
        first_object_fields = {
            first_object.text: self.post.text,
            first_object.author: self.user,
            first_object.group: self.group,
        }
        for item, expected in first_object_fields.items():
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
        for i in range(1, 14):
            cls.post = Post.objects.create(
                id=i,
                text='Тестовый текст',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Тестирование паджинатора. На первой странице 10 объектов."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj')), 10)

    def test_second_page_contains_three_records(self):
        """Тестирование паджинатора. На второй странице 3 объекта."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj')), 3)
