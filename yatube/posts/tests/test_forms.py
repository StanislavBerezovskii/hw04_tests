from django.test import Client, TestCase
from django.urls import reverse

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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'author': self.user,
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
        added_post = Post.objects.first()
        self.assertEqual(added_post.text, form_data['text'])
        self.assertEqual(added_post.group.pk, form_data['group'])
        self.assertEqual(added_post.author, self.user)

    def test_edit_post(self):
        post_count = Post.objects.count()
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
        new_version = Post.objects.get(id=self.post.id)
        self.assertEqual(new_version.text, form_data['text'])
        self.assertEqual(new_version.group, new_group)
        guest_client = Client()
        response = guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('users:login') + '?next='
                             + reverse('posts:post_edit',
                             kwargs={'post_id': f'{self.post.id}'}))
        self.assertEqual(Post.objects.count(), post_count)
