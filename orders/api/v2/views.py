# from rest_framework import viewsets
# from rest_framework.permissions import IsAuthenticated
#
# from pagination import StandardResultsSetPagination
# from permissions import IsAdminOrOwner
# from .serializers import OrderSerializerV2
# from ...models import Order
#
#
# class OrderViewSetV2(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializerV2
#     http_method_names = ['get', 'post']
#     pagination_class = StandardResultsSetPagination
#
#     def get_permissions(self):
#         if self.action == 'retrieve':
#             return [IsAuthenticated(), IsAdminOrOwner()]
#         return [IsAuthenticated(), ]
#
#     def list(self, request, *args, **kwargs):
#         if request.user.is_superuser:
#             orders = Order.objects.all().order_by('-created_at')
#         else:
#             orders = Order.objects.filter(user=request.user).order_by('-created_at')
#         page = self.paginate_queryset(orders)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#         else:
#             serializer = self.get_serializer(orders, many=True)
#         return self.get_paginated_response(serializer.data)
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
