# deals/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Group, Post


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')

        cls.COUNT_OF_POSTS = 13
        cls.COUNT_ON_PAGE = 10
        cls.OTHERS_OF_POSTS = 3
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        for _ in range(0, cls.COUNT_OF_POSTS):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )
        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': cls.user}): 'posts/profile.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_first_page_contains_ten_records(self):
        for reverse_name in (PaginatorViewsTest.
                             templates_pages_names.keys()):
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    PaginatorViewsTest.COUNT_ON_PAGE)

    def test_second_page_contains_three_records(self):
        for reverse_name in (PaginatorViewsTest.
                             templates_pages_names.keys()):
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 PaginatorViewsTest.OTHERS_OF_POSTS)


User = get_user_model()


class TaskPagesTests(TestCase):
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
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskPagesTests.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': TaskPagesTests.user}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': TaskPagesTests.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={
                'post_id': TaskPagesTests.post.pk}): 'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # # Проверка словаря контекста главной страницы (в нём передаётся форма)
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_object = response.context['page_obj'][0]
        task_title_0 = first_object.author
        task_text_0 = first_object.text
        self.assertEqual(task_title_0, TaskPagesTests.user)
        self.assertEqual(task_text_0, 'Тестовый пост')

    def test_group_posts_pages_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list', kwargs={
                        'slug': 'test-slug'})))
        first_object = response.context['page_obj'][0]
        task_title_0 = first_object.author
        task_text_0 = first_object.text
        task_group_0 = first_object.group
        self.assertEqual(task_title_0, TaskPagesTests.user)
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_group_0.slug, 'test-slug')

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:profile', kwargs={
                        'username': TaskPagesTests.user})))
        first_object = response.context['page_obj'][0]
        task_title_0 = first_object.author
        task_text_0 = first_object.text
        task_group_0 = first_object.group
        author = response.context['author']
        self.assertEqual(task_title_0, TaskPagesTests.user)
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertEqual(task_group_0.slug, 'test-slug')
        self.assertEqual(author, TaskPagesTests.user)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail', kwargs={
                        'post_id': TaskPagesTests.post.pk})))
        self.assertEqual(response.context['post'].author, TaskPagesTests.user)
        self.assertEqual(response.context['post'].text, 'Тестовый пост')

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': TaskPagesTests.post.pk}))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        is_edit = response.context.get('is_edit')
        self.assertTrue(is_edit)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
