# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from rest_framework import status

from posts.models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.url = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{TaskURLTests.user}/': 'posts/profile.html',
            f'/posts/{TaskURLTests.post.pk}/': 'posts/post_detail.html',
            f'/posts/{TaskURLTests.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        cls.url_guest_client = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/profile/{TaskURLTests.user}/': 'posts/profile.html',
            f'/posts/{TaskURLTests.post.pk}/': 'posts/post_detail.html',
        }

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(TaskURLTests.user)

    def test_urls_uses_correct_template_and_url(self):
        """URL-адрес использует соответствующий шаблон и
         доступен авторизованному пользователю."""

        for address, template in TaskURLTests.url.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю."""

        for address in TaskURLTests.url_guest_client.keys():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Проверяем доступность страниц для авторизованного пользователя
    # def test_task_list_url_exists_at_desired_location(self):
    #     """Страница /posts/<int:post_id>/edit/ доступна автору публикации."""
    #     response = self.authorized_client.get(
    #         f'/posts/{TaskURLTests.post.pk}/edit/')
    #     self.assertEqual(response.status_code, 200)

    # def test_task_detail_url_exists_at_desired_location_authorized(self):
    #     """Страница /create/ доступна авторизованному
    #     пользователю."""
    #     response = self.authorized_client.get('/create/')
    #     self.assertEqual(response.status_code, 200)
