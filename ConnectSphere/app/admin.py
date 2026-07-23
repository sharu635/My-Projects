from django.contrib import admin
from .models import Profile, Post, Comment, Like, Follow


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'date_joined')
    search_fields = ('user__username', 'bio')
    list_filter = ('date_joined',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption_preview', 'created_date', 'likes_count', 'comments_count')
    search_fields = ('user__username', 'caption')
    list_filter = ('created_date',)

    def caption_preview(self, obj):
        return obj.caption[:80] if obj.caption else '(No caption)'
    caption_preview.short_description = 'Caption'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'text_preview', 'created_date')
    search_fields = ('user__username', 'text')
    list_filter = ('created_date',)

    def text_preview(self, obj):
        return obj.text[:80]
    text_preview.short_description = 'Comment'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'liked_date')
    search_fields = ('user__username',)
    list_filter = ('liked_date',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'follow_date')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('follow_date',)
