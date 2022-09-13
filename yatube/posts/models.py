from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Название',
                             help_text='Введите название группы',
                             max_length=200)
    slug = models.SlugField(verbose_name='URL-Адрес',
                            help_text='Введите URL-адрес группы',
                            unique=True)
    description = models.TextField(verbose_name='Описание',
                                   help_text='Введите описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст', help_text='Введите текст поста',)
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации', auto_now_add=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        help_text='Укажите группу для поста',
        verbose_name='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]
