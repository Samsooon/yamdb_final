from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import QueryDict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Comment, Genre, Review, Title, User

from .filters import TitleFilters
from .mixins import ListCreateDestroyMixin
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorModeratorAdminSuperuser)
from .serializers import (AdminUserSerializer, CategorySerializer,
                          CommentSerializer, GenreSerializer,
                          ReviewsSerializer, SafeMethodTitleSerializer,
                          SignupSerializer, TitleSerializer, TokenSerializer,
                          UserSerializer)


class AbstractViewSet(ListCreateDestroyMixin):
    serializer_class = ...
    queryset = ...
    permission_classes = [IsAdminOrReadOnly, ]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    class Meta:
        abstract = True


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = [
        IsAuthorModeratorAdminSuperuser,
        IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self):
        queryset = Comment.objects.filter(
            review_id=self.kwargs['review_id'])
        return queryset

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)


class ReviewsViewSet(ModelViewSet):
    serializer_class = ReviewsSerializer
    pagination_class = PageNumberPagination
    permission_classes = [
        IsAuthorModeratorAdminSuperuser,
        IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.review.all()

    def create(self, request, *args, **kwargs):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer = ReviewsSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            if title.review.filter(author=self.request.user).exists():

                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer.save(author=self.request.user, title=title)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GenreViewSet(AbstractViewSet):
    serializer_class = GenreSerializer
    queryset = Genre.objects.all()


class CategoryViewSet(AbstractViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all().annotate(Avg('review__score'))
    permission_classes = [IsAdminOrReadOnly, ]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = TitleFilters

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return SafeMethodTitleSerializer
        return TitleSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = (IsAdmin, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False, methods=['get', 'patch'],
        url_path='me', url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def about_me(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


def send_confirmation_code(user):
    user.confirmation_code = default_token_generator.make_token(user)
    user.save()
    subject = 'Код подтверждения YaMDb'
    message = f'{user.confirmation_code} - ваш код для авторизации на YaMDb'
    admin_email = 'admin@yamdb.ru'
    user_email = [user.email]
    return send_mail(subject, message, admin_email, user_email)


@permission_classes([AllowAny])
class UserRegView(APIView):
    def post(self, request):
        data = request.data
        serializer = SignupSerializer(data=data)
        if isinstance(data, QueryDict):
            data = data.dict()
        if User.objects.filter(**data).exists():
            user = User.objects.get(**data)
            if user.last_login and user.confirmation_code:
                return Response(
                    'Учетная запись уже активирована',
                    status=status.HTTP_200_OK
                )
            send_confirmation_code(user)
            return Response(serializer.initial_data, status=status.HTTP_200_OK)
        else:
            if serializer.is_valid():
                user, created = User.objects.update_or_create(
                    **serializer.validated_data
                )
                send_confirmation_code(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


@permission_classes([AllowAny])
class GetTokenView(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        username = serializer.data['username']
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.data['confirmation_code']
        if not default_token_generator.check_token(user, confirmation_code):
            return Response({'Wrong Code'}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
        return Response({'token': str(token.access_token)},
                        status=status.HTTP_200_OK)
