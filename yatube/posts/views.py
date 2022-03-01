from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import pages


@cache_page(20, key_prefix='index_page')
def index(request):
    posts = Post.objects.all()
    page_obj = pages(request, posts, settings.POSTS_NUM)
    template = 'posts/index.html'
    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': page_obj
    }
    cache.clear()
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pages(request, posts, settings.POSTS_NUM)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()
    posts_count = posts.count()
    page_obj = pages(request, posts, settings.POSTS_NUM)
    template_name = 'posts/profile.html'
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=user
        ).exists()
    else:
        following = False
    context = {
        'posts_count': posts_count,
        'page_obj': page_obj,
        'username': user,
        'following': following
    }
    return render(request, template_name, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template_name = 'posts/post_detail.html'
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, template_name, context)


@login_required
def post_create(request):
    template_name = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(request, template_name, {'form': form})


@login_required
def post_edit(request, post_id):
    template_name = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': True
    }
    if request.user.id != post.author.id:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)
    return render(request, template_name, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    user = request.user
    following = Follow.objects.filter(user=user)
    auth_list = []
    for auth in following:
        auth_list.append(auth.author)
    posts = Post.objects.all().filter(author__in=auth_list)
    page_obj = pages(request, posts, settings.POSTS_NUM)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    auth = get_object_or_404(User, username=username)
    user = request.user
    if user == auth or Follow.objects.filter(user=user, author=auth).exists():
        return redirect('posts:index')
    else:
        Follow.objects.create(user=user, author=auth)
        return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    auth = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(user=user, author=auth).delete()
    return redirect('posts:profile', username=auth)
