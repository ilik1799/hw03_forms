from django.shortcuts import get_object_or_404, render

from .models import Group, Post

POST_OBJ = 10


def index(request):
    posts = Post.objects.select_related('group')[:POST_OBJ]
    context = {
        'posts': posts,
        'title': 'Это главная страница проекта Yatube'
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POST_OBJ]
    context = {
        'group': group,
        'posts': posts,
        'title': 'Здесь будет информация о группах проекта Yatube'
    }
    return render(request, 'posts/group_list.html', context)
