from api_yamdb.settings import RATING_SCORE
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import year_validator


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES_CHOICES = (
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь')
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Электронная почта'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    confirmation_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Код для авторизации',
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True)
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True)

    role = models.CharField(
        max_length=30,
        choices=ROLES_CHOICES,
        default='user',
        verbose_name='Роль пользователя'
    )

    @property
    def is_admin(self):
        return self.role == User.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR or self.is_staff

    def __str__(self) -> str:
        return self.username


class AbstractModel(models.Model):
    """Абстрактная Модель"""
    name = models.CharField(max_length=256)
    slug = models.SlugField(
        max_length=50,
        unique=True,
        null=False,
        blank=False
    )

    class Meta:
        abstract = True


class Genre(AbstractModel):
    """Модель Жанра."""

    def __str__(self):
        return self.name


class Category(AbstractModel):
    """Модель Категории."""

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(max_length=256)
    year = models.IntegerField(validators=[year_validator])
    description = models.TextField()
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles'
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель Жанр произведения."""
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        default=None
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        default=None
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_genre_title'
            )
        ]

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='review')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='review')
    score = models.IntegerField(
        validators=[
            MaxValueValidator(RATING_SCORE['max']),
            MinValueValidator(RATING_SCORE['min'])
        ]
    )
    pub_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='one_review_by_title_for_user')
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text
