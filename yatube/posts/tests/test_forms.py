from posts.forms import PostForm
from posts.models import Group, Post
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

User = get_user_model()


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        # Создаем запись в базе данных для проверки сушествующего slug
        # Создаем форму, если нужна проверка атрибутов
        cls.form = PostForm()
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        # Создаем неавторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskCreateFormTests.user)

    def test_create_task(self):
        """Валидная форма создает запись в Task."""
        # Подсчитаем количество записей в Task
        tasks_count = Post.objects.count()
        # Для тестирования загрузки изображений
        # берём байт-последовательность картинки,
        # состоящей из двух пикселей: белого и чёрного

        form_data = {
            'text': 'Тестовый текст',
            'author': TaskCreateFormTests.user,
        }
        # Отправляем POST-запрос
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        # self.assertEqual(response.status_code, 200)
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                author=TaskCreateFormTests.user,
            ).exists()
        )

    def test_post_edit(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': TaskCreateFormTests.group.id,
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(TaskCreateFormTests.post.id,)),
            follow=True,
            data=form_data
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст',
                author=TaskCreateFormTests.user,
                group=TaskCreateFormTests.group.id,
            ).exists()
        )

    def test_redirect(self):
        response = self.guest_client.get(
            reverse('posts:post_edit', args=(TaskCreateFormTests.post.id,)),
            follow=True
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        redirect_url = (
            reverse('users:login') + '?next='
            + reverse('posts:post_edit', args=(TaskCreateFormTests.post.id,))
        )
        self.assertRedirects(response, redirect_url)
