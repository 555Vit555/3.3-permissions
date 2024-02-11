from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement
from advertisements.permissions import IsCreatorOrReadOnly
from advertisements.serializers import AdvertisementSerializer


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    # TODO: настройте ViewSet, укажите атрибуты для кверисета,
    #   сериализаторов и фильтров
    serializer_class = AdvertisementSerializer

    filter_backends = [DjangoFilterBackend, ]
    filterset_class = AdvertisementFilter
    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "update", "partial_update"]:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        us = self.request.user
        queryset = Advertisement.objects.exclude(status="DRAFT")
        queryset_draft = Advertisement.objects.filter(status="DRAFT", creator=us.id)
        if self.request.user.is_authenticated:
            queryset = queryset | queryset_draft
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(methods=['post'], detail=True, url_path='toggle_favorite')
    def favorite(self, request, *args, **kwargs):
        post = self.get_object()
        user = request.user
        if user.favorites.filter(id=post.id).exists():
            user.favorites.remove(post)
        else:
            if post.creator != user:
                user.favorites.add(post)
        return Response({'status': user.favorites.filter(id=post.id).exists()})


