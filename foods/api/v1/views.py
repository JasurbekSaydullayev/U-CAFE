from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import FoodSerializer, FoodDetailSerializer, PhotoSerializer
from foods.models import Food, Photo

from pagination import StandardResultsSetPagination


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action in ['list', 'delete']:
            return FoodSerializer
        elif self.action in ['retrieve', 'partial_update', 'update', 'create']:
            return FoodDetailSerializer

    def list(self, request, *args, **kwargs):
        category = request.query_params.get('category')
        if category:
            foods = Food.objects.filter(category=category).all().order_by('-created_at')
        else:
            foods = Food.objects.all().order_by('-created_at')
        page = self.paginate_queryset(foods)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(foods, many=True)
            return Response(serializer.data)


class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    parser_classes = (MultiPartParser, FormParser)
    http_method_names = ['post', 'put', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
