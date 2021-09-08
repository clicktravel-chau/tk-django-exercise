from rest_framework import viewsets

from core.models import Recipe

from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in database"""
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer

    def get_queryset(self):
        """Retrieve recipes"""
        name = self.request.query_params.get('name')
        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__contains=name)

        return queryset.order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new recipe"""
        serializer.save()
