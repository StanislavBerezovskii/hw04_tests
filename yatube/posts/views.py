# posts/views.py
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings as s

from .models import Post, Group, User
from .forms import PostForm


def pagination(request, queryset):
    request = request.GET.get('page')
    paginator = Paginator(queryset, s.PER_PAGE)
    page_obj = paginator.get_page(request)
    return page_obj


def index(request):
    post_list = Post.objects.all()
    context = {
        'page_obj': pagination(request, post_list)
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
        'page_obj': pagination(request, post_list),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    post_author = get_object_or_404(User, username=username)
    post_list = post_author.posts.all()
    post_count = post_list.count()
    context = {
        'page_obj': pagination(request, post_list),
        'username': username,
        'post_count': post_count,
        'post_author': post_author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    this_post = get_object_or_404(Post, id=post_id)
    author_post_count = this_post.author.posts.count()
    context = {
        'this_post': this_post,
        'author_post_count': author_post_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    author = post.author
    if author != user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': post,
    }
    return render(request, 'posts/create_post.html', context)
