from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from permissions import IsCook, IsSellerOrCook
from .serializers import FoodSerializer, FoodDetailSerializer
from foods.models import Food

from pagination import StandardResultsSetPagination


class FoodViewSet(viewsets.ModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    pagination_class = StandardResultsSetPagination
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.action in ['list', 'delete']:
            return FoodSerializer
        elif self.action in ['retrieve', 'partial_update', 'update', 'create']:
            return FoodDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated(), IsSellerOrCook()]
        return [IsAuthenticated(), IsCook()]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'image', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Upload image'
        )
    ])
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('category', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING, format='string',
                          description='Category'),
    ])
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
