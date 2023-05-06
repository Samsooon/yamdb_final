from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Юзера."""

    list_display = (
        'pk',
        'username',
        'email',
        'role',
        'is_superuser',
        'bio',
        'first_name',
        'last_name',
    )
    list_editable = ('role',)
    search_fields = ('username', 'role',)
    empty_value_display = '-пусто-'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Category."""

    list_display = (
        'pk',
        'name',
        'slug'
    )
    search_fields = ('slug',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Genre."""

    list_display = (
        'pk',
        'name',
        'slug'
    )
    search_fields = ('slug',)
    list_filter = ('slug',)
    empty_value_display = '-пусто-'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Title."""

    list_display = (
        'pk',
        'name',
        'year',
        'genre_info',
        'category',
        'description'
    )
    search_fields = ('name',)
    list_filter = ('category',)
    empty_value_display = '-пусто-'

    def genre_info(self, object):
        return ", ".join([genre.name for genre in object.genre.all()])

    genre_info.short_description = 'Жанры'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Review."""

    list_display = (
        'pk',
        'text',
        'author',
        'pub_date',
        'title',
        'score'
    )
    search_fields = ('title',)
    list_filter = ('author', 'title')
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Настройки админ панели для модели Comment."""

    list_display = (
        'pk',
        'text',
        'author',
        'pub_date',
        'review'
    )
    search_fields = ('review',)
    list_filter = ('author', 'review')
    empty_value_display = '-пусто-'
