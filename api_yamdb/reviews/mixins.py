from rest_framework.viewsets import GenericViewSet, mixins


class ListCreateDestroyMixin(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    pass
