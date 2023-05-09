from django.urls import include, path
from rest_framework.routers import DefaultRouter
from reviews.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                           GetTokenView, ReviewsViewSet, TitleViewSet,
                           UserRegView, UserViewSet)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(
    r'titles',
    TitleViewSet,
    basename='title'
)
router_v1.register(
    r'genres',
    GenreViewSet,
    basename='genres'
)
router_v1.register(
    r'categories',
    CategoryViewSet,
    basename='categories'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewsViewSet, basename='review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
router_v1.register('users', UserViewSet, basename='user')


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', UserRegView.as_view(), name='auth_signup'),
    path('v1/auth/token/', GetTokenView.as_view(), name='token'),
]
