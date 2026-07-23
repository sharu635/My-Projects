from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Profile, Post, Comment, Like, Follow
from .forms import RegistrationForm, LoginForm, ProfileForm, PostForm, CommentForm


def register(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to ConnectSphere, {user.first_name}!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def home(request):
    """Display the home feed with all posts, newest first."""
    posts = Post.objects.select_related('user', 'user__profile').prefetch_related('likes', 'comments').all()
    # Add is_liked attribute for template use
    for post in posts:
        post.is_liked = post.likes.filter(user=request.user).exists()
    search_query = request.GET.get('q', '')
    return render(request, 'home.html', {'posts': posts, 'search_query': search_query})


@login_required
def search_users(request):
    """Search users by username or name."""
    query = request.GET.get('q', '')
    users = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).select_related('profile').exclude(id=request.user.id)
    return render(request, 'search_results.html', {'users': users, 'query': query})


@login_required
def profile(request, username):
    """Display a user's profile."""
    profile_user = get_object_or_404(User, username=username)
    profile_obj = get_object_or_404(Profile, user=profile_user)
    posts = Post.objects.filter(user=profile_user).select_related('user', 'user__profile')
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    followers_count = profile_user.followers_set.count()
    following_count = profile_user.following_set.count()
    posts_count = posts.count()
    context = {
        'profile_user': profile_user,
        'profile': profile_obj,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'posts_count': posts_count,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    """Edit the current user's profile."""
    profile_obj = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile_obj)
        if form.is_valid():
            profile_instance = form.save()
            # Update User model fields
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile_obj, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })
    return render(request, 'edit_profile.html', {'form': form})


@login_required
def create_post(request):
    """Create a new post."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', pk=post.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})


@login_required
def post_detail(request, pk):
    """View a single post with comments and likes."""
    post = get_object_or_404(Post.objects.select_related('user', 'user__profile'), pk=pk)
    comments = post.comments.select_related('user', 'user__profile').all()
    comment_form = CommentForm()
    is_liked = post.likes.filter(user=request.user).exists()
    likes_count = post.likes_count
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'likes_count': likes_count,
    }
    return render(request, 'post_detail.html', context)


@login_required
def edit_post(request, pk):
    """Edit an existing post. Only the post owner can edit."""
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        messages.error(request, 'You can only edit your own posts.')
        return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, pk):
    """Delete a post. Only the post owner can delete."""
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        messages.error(request, 'You can only delete your own posts.')
        return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    return redirect('post_detail', pk=pk)


@login_required
def add_comment(request, post_pk):
    """Add a comment to a post."""
    post = get_object_or_404(Post, pk=post_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'Comment added!')
    return redirect('post_detail', pk=post_pk)


@login_required
def edit_comment(request, pk):
    """Edit a comment. Only the comment owner can edit."""
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user != request.user:
        messages.error(request, 'You can only edit your own comments.')
        return redirect('post_detail', pk=comment.post.pk)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            comment.text = text
            comment.save()
            messages.success(request, 'Comment updated!')
        else:
            messages.error(request, 'Comment cannot be empty.')
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def delete_comment(request, pk):
    """Delete a comment. Only the comment owner can delete."""
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    if comment.user != request.user:
        messages.error(request, 'You can only delete your own comments.')
        return redirect('post_detail', pk=post_pk)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted!')
    return redirect('post_detail', pk=post_pk)


@login_required
def like_post(request, pk):
    """Toggle like/unlike on a post. Returns JSON for AJAX."""
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            # Already liked, so unlike
            like.delete()
            liked = False
        else:
            liked = True
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'liked': liked,
                'likes_count': post.likes.count()
            })
        return redirect('post_detail', pk=pk)
    return redirect('post_detail', pk=pk)


@login_required
def follow_user(request, username):
    """Toggle follow/unfollow a user. Returns JSON for AJAX."""
    target_user = get_object_or_404(User, username=username)
    if request.user == target_user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)
        messages.error(request, 'You cannot follow yourself.')
        return redirect('profile', username=username)
    if request.method == 'POST':
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=target_user
        )
        if not created:
            follow.delete()
            is_following = False
        else:
            is_following = True
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'is_following': is_following,
                'followers_count': target_user.followers_set.count()
            })
        return redirect('profile', username=username)
    return redirect('profile', username=username)


@login_required
def followers_list(request, username):
    """Display a user's followers."""
    profile_user = get_object_or_404(User, username=username)
    follow_objects = Follow.objects.filter(following=profile_user).select_related('follower', 'follower__profile')
    followers = [f.follower for f in follow_objects]
    return render(request, 'followers.html', {
        'profile_user': profile_user,
        'followers': followers,
    })


@login_required
def following_list(request, username):
    """Display users that a user is following."""
    profile_user = get_object_or_404(User, username=username)
    follow_objects = Follow.objects.filter(follower=profile_user).select_related('following', 'following__profile')
    following = [f.following for f in follow_objects]
    return render(request, 'following.html', {
        'profile_user': profile_user,
        'following': following,
    })


@login_required
def dashboard(request):
    """User dashboard with posts, liked posts, followers, and following."""
    active_tab = request.GET.get('tab', 'posts')
    user_posts = Post.objects.filter(user=request.user).select_related('user', 'user__profile')
    liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    liked_posts = Post.objects.filter(id__in=liked_post_ids).select_related('user', 'user__profile')
    followers_objs = Follow.objects.filter(following=request.user).select_related('follower', 'follower__profile')
    following_objs = Follow.objects.filter(follower=request.user).select_related('following', 'following__profile')
    followers = [f.follower for f in followers_objs]
    following = [f.following for f in following_objs]
    context = {
        'user_posts': user_posts,
        'liked_posts': liked_posts,
        'followers': followers,
        'following': following,
        'active_tab': active_tab,
    }
    return render(request, 'dashboard.html', context)
