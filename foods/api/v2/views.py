# from rest_framework.response import Response
# from rest_framework import viewsets
# from rest_framework.permissions import AllowAny
#
from pagination import StandardResultsSetPagination
# from .serializers import FoodSerializerV2, FoodDetailSerializerV2
# from ...models import Food
#
#
# class FoodViewSetV2(viewsets.ModelViewSet):
#     queryset = Food.objects.all()
#     http_method_names = ['get']
#     permission_classes = [AllowAny]
#     pagination_class = StandardResultsSetPagination
#
#     def get_serializer_class(self):
#         if self.action == 'list':
#             return FoodSerializerV2
#         elif self.action == 'retrieve':
#             return FoodDetailSerializerV2
#
#     def list(self, request, *args, **kwargs):
#         category = request.query_params.get('category', None)
#         if category:
#             foods = Food.objects.filter(category=category).all().order_by('-created_at')
#         else:
#             foods = self.get_queryset().order_by('-created_at', 'category')
#         page = self.paginate_queryset(foods)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         else:
#             serializer = self.get_serializer(foods, many=True)
#             return Response(serializer.data)
