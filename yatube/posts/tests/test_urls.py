from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group

User = get_user_model()


class URLTests(TestCase):
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
            author=cls.user
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    # Проверяем общедоступные страницы
    def test_free_access_pages(self):
        """Страницы /, /group/<slug>/, /profile/<username>/ и /posts/<post_id>
        доступны любому пользователю."""
        free_access_url_list = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.post.author}/',
            f'/posts/{self.post.id}/'
        ]
        for url in free_access_url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_restricted_access_pages(self):
        """Страницы /create/ и /posts/<post_id>/edit/>
        доступны только авторизованным пользователям."""
        restricted_access_url_list = [
            '/create/',
            f'/posts/{self.post.id}/edit/'
        ]
        for url in restricted_access_url_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_restricted_access_pages_redirect(self):
        """Страницы /create/ и /posts/<post_id>/edit/> перенаправляют
        неавторизованных пользователей на страницу авторизации."""
        restricted_access_url_list = [
            '/create/',
            f'/posts/{self.post.id}/edit/'
        ]
        for url in restricted_access_url_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_create_redirects_not_author(self):
        """Страница /posts/<post_id>/edit/> перенаправляет
        авторизованного пользователя на страницу поста, если тот не автор."""
        foreign_author = User.objects.create_user(username='SomeDude')
        foreign_post = Post.objects.create(
            text='Чужой пост',
            author=foreign_author
        )
        response = self.authorized_client.get(
            f'/posts/{foreign_post.id}/edit/', follow=True)
        self.assertRedirects(response, f'/posts/{foreign_post.id}/')

    def test_urls_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_non_existant_page_404(self):
        """При запросе неусществующего URL-адреса происходит ошибка 404."""
        url = '/unexisting_page/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
