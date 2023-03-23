# posts/views.py
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Post, Group, User
from .forms import PostForm
from yatube.constants import POSTS_PER_STR
from .utils import create_page_object


def index(request):
    post_list = Post.objects.all()

    page_obj = create_page_object(request, post_list, POSTS_PER_STR)

    context = {
        'title': settings.TITLE_INDEX,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = create_page_object(request, post_list, POSTS_PER_STR)

    context = {
        'group': group,
        'page_obj': page_obj,

    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author')
    posts_count = Post.objects.filter(author__exact=author).count
    page_obj = create_page_object(request, post_list, POSTS_PER_STR)

    context = {
        'author': author,
        'title': settings.TITLE_INDEX,
        'page_obj': page_obj,
        'posts_count': posts_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_list = post.author.posts.all()
    page_obj = create_page_object(request, post_list, POSTS_PER_STR)
    posts_count = Post.objects.filter(author__exact=post.author).count
    is_edit = request.user == post.author
    context = {
        'post': post,
        'title': settings.TITLE_INDEX,
        'page_obj': page_obj,
        'is_edit': is_edit,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    post_form = PostForm(request.POST or None)
    template = 'posts/create_post.html'
    if post_form.is_valid():
        post = post_form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)

    context = {
        'form': post_form,
        'is_edit': False
    }
    return render(request, template, {'form': context})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if not request.user == post.author:
        return redirect('posts:post_detail', post.author)

    post_form = PostForm(request.POST or None, instance=post)
    template = 'posts/create_post.html'
    if post_form.is_valid():
        post_form.save()
        return redirect('posts:post_detail', post_id)

    return render(request, template, {'form': post_form, 'is_edit': True})
