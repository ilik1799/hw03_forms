from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Идентификатор', unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Group'

    def __str__(self):
        return self.title


class Post(models.Model):
    def __str__(self):
        return self.text[:15]

    text = models.TextField('Описание')
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )

    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )

    class Meta:
        ordering = ('-pub_date',)
