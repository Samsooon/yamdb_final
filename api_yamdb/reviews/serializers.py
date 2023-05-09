import re

from api_yamdb.settings import RATING_SCORE
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.response import Response

from reviews.models import Category, Comment, Genre, Review, Title, User


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment


class ReviewsSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        read_only=True, slug_field='name'
    )
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    score = serializers.IntegerField(
        validators=[
            MaxValueValidator(RATING_SCORE['max']),
            MinValueValidator(RATING_SCORE['min'])
        ]
    )

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date',)
        model = Review
        read_only_fields = ('author', 'title')
        extra_kwargs = {'title': {'required': True},
                        'author': {'required': True}}

    def validate_title_exists(self):
        if not Title.objects.filter(
            title_pk=self.request.data['title_id']
        ).exists():
            return Response({'Ошибка': "Title не найден"})

    def validate_dup(self, request, data):
        if Review.objects.get(
            author=request.user,
            title=self.data['title']
        ).exists():
            raise ValidationError('Уже есть')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class SafeMethodTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='review__score__avg',
        read_only=True
    )
    category = CategorySerializer()
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        exclude = []


class ValidateUserSerializer(serializers.ModelSerializer):

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" не разрешено.'
            )
        if not re.match(r'[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                f'{value} содержит запрещённые символы.'
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                'Имя пользователя не может быть больше 150 символов.'
            )
        return value


class UserSerializer(ValidateUserSerializer):
    username = serializers.CharField(required=True, max_length=150)
    email = serializers.CharField(required=True, max_length=254)
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )
        ordering = ['-pk']

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                "Имя пользователя Me не разрешено"
            )
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                "Имя пользователя содержит запрещенные символы"
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                'Имя пользователя не может содержать более 150 символов'
            )
        return value


class AdminUserSerializer(ValidateUserSerializer):

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )
        ordering = ['-pk']


class SignupSerializer(ValidateUserSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')
        ordering = ['-pk']


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
