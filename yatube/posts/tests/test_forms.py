from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.pk,
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.post.author.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        new_group = Group.objects.create(
            title='Новая тестовая группа',
            slug='new-test-slug',
            description='Новое тестовое описание',
        )
        form_data = {
            'group': new_group.pk,
            'text': 'Новый тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        new_version = Post.objects.filter(id=self.post.id)[0]
        self.assertEqual(new_version.text, 'Новый тестовый текст')
        self.assertEqual(new_version.group, new_group)
