from django.contrib import admin

from .models import Post, Group


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description',
        'slug')
    search_fields = ('title', 'description',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
