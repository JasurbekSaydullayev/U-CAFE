import pandas as pd
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from permissions import IsAdmin, IsManager
from .views import (
    IncomeAPIView, GetDiscountOrders, ExpensesAPIView, SalesAPIView,
    PaymentMethodsStatsAPIView, PopularCategoriesStatsAPIView,
    GetHistoryOrders, SalesReportView, SalesByDayOfWeekAPIView, GetCancelledOrders
)

def get_data(view_class, request):
    view_instance = view_class()
    view_response = view_instance.dispatch(request._request)
    return view_response.data

class GetExcel(APIView):
    permission_classes = (IsAuthenticated, IsManager)

    def get(self, request, *args, **kwargs):

        data1 = get_data(IncomeAPIView, request)
        data2 = get_data(GetDiscountOrders, request)
        data3 = get_data(ExpensesAPIView, request)
        data4 = get_data(SalesAPIView, request)
        data5 = get_data(PaymentMethodsStatsAPIView, request)
        data6 = get_data(GetHistoryOrders, request)
        data7 = get_data(SalesReportView, request)
        data8 = get_data(SalesByDayOfWeekAPIView, request)
        data9 = get_data(GetCancelledOrders, request)
        data10 = get_data(PopularCategoriesStatsAPIView, request)

        # Har bir ma'lumotni DataFrame'ga o'girib, indeks ko'rsatish
        df1 = pd.DataFrame([data1]) if isinstance(data1, dict) else pd.DataFrame(data1)
        df2 = pd.DataFrame([data2]) if isinstance(data2, dict) else pd.DataFrame(data2)
        df3 = pd.DataFrame([data3]) if isinstance(data3, dict) else pd.DataFrame(data3)
        df4 = pd.DataFrame([data4]) if isinstance(data4, dict) else pd.DataFrame(data4)
        df5 = pd.DataFrame([data5]) if isinstance(data5, dict) else pd.DataFrame(data5)
        df6 = pd.DataFrame([data6]) if isinstance(data6, dict) else pd.DataFrame(data6)
        df7 = pd.DataFrame([data7]) if isinstance(data7, dict) else pd.DataFrame(data7)
        df8 = pd.DataFrame([data8]) if isinstance(data8, dict) else pd.DataFrame(data8)
        df9 = pd.DataFrame([data9]) if isinstance(data9, dict) else pd.DataFrame(data9)
        df10 = pd.DataFrame([data10]) if isinstance(data10, dict) else pd.DataFrame(data10)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=combined_statistics.xlsx'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df1.to_excel(writer, sheet_name='Income', index=False)
            df2.to_excel(writer, sheet_name='DiscountOrders', index=False)
            df3.to_excel(writer, sheet_name='Expenses', index=False)
            df4.to_excel(writer, sheet_name='Sales', index=False)
            df5.to_excel(writer, sheet_name='PaymentMethods', index=False)
            df6.to_excel(writer, sheet_name='OrderHistory', index=False)
            df7.to_excel(writer, sheet_name='SalesReport', index=False)
            df8.to_excel(writer, sheet_name='SalesByDayOfWeek', index=False)
            df9.to_excel(writer, sheet_name='CancelOrders', index=False)
            df10.to_excel(writer, sheet_name='PopularCategories', index=False)

        return response
