import pandas as pd
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from openpyxl.styles import Alignment
from permissions import IsManager
from .serializers import FileUploadSerializer
from .views import (
    IncomeAPIView, GetDiscountOrders, ExpensesAPIView, SalesAPIView,
    PaymentMethodsStatsAPIView, PopularCategoriesStatsAPIView,
    GetHistoryOrders, SalesReportView, SalesByDayOfWeekAPIView, GetCancelledOrders
)
from ...DRY import dry
from ...models import Order


def get_data(view_class, request):
    view_instance = view_class()
    view_response = view_instance.dispatch(request._request)
    return view_response.data


class GetExcel(APIView):
    permission_classes = (IsAuthenticated, IsManager)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format='date',
                description='Start date in YYYY-MM-DD format'
            ),
            openapi.Parameter(
                'end_date',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format='date',
                description='End date in YYYY-MM-DD format'
            ),
        ],
        responses={
            status.HTTP_200_OK: openapi.Response(
                description='Excel faylni qaytaradi',
                content={
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': openapi.Schema(
                        type=openapi.TYPE_FILE
                    )
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        start_date, end_date, previous_start_date, previous_end_date = dry(request)
        data1 = get_data(IncomeAPIView, request)
        data2 = Order.objects.filter(discount__gt=0, created_at__range=(start_date, end_date)).order_by('-created_at')
        data3 = get_data(ExpensesAPIView, request)
        data4 = get_data(SalesAPIView, request)
        data5 = get_data(PaymentMethodsStatsAPIView, request)
        data6 = get_data(GetHistoryOrders, request)
        data9 = Order.objects.filter(status='Cancelled',
                                     created_at__range=(start_date, end_date)).all().order_by(
            '-created_at')
        data10 = get_data(PopularCategoriesStatsAPIView, request)

        # Process and prepare data
        data6.pop('next', None)
        data6.pop('previous', None)
        data6.pop('count', None)
        data6 = data6.get('results', [])

        if isinstance(data6, list):
            for entry in data6:
                entry.pop('payments', None)
                entry.pop('items', None)
                entry.pop('delivery_status', None)

        # Convert data to DataFrames
        df1 = pd.DataFrame([data1]) if isinstance(data1, dict) else pd.DataFrame(data1)
        df2 = pd.DataFrame(list(data2.values(
            'user', 'order_type', 'position', 'full_price', 'status_pay', 'status', 'discount', 'created_at'
        )))
        df3 = pd.DataFrame([data3]) if isinstance(data3, dict) else pd.DataFrame(data3)
        df4 = pd.DataFrame([data4]) if isinstance(data4, dict) else pd.DataFrame(data4)
        df5 = pd.DataFrame([data5]) if isinstance(data5, dict) else pd.DataFrame(data5)
        df6 = pd.DataFrame([data6]) if isinstance(data6, dict) else pd.DataFrame(data6)
        df9 = pd.DataFrame([data9]) if isinstance(data9, dict) else pd.DataFrame(data9)
        df10 = pd.DataFrame([data10]) if isinstance(data10, dict) else pd.DataFrame(data10)

        if 'created_at' in df2.columns:
            df2['created_at'] = df2['created_at'].apply(lambda x: x.replace(tzinfo=None) if pd.notnull(x) else x)

        df1.rename(columns={
            'total_income': 'Общий доход',
            'percentage_change_income': 'Прибыль в процентах по сравнению с предыдущим периодом',
            'total_trade': 'Общий объем продаж',
            'percentage_change_trade': 'Продажи указаны в процентах по сравнению с предыдущим периодом.'
        }, inplace=True)
        df2.rename(columns={
            'user': 'Продавец',
            'order_type': "Тип заказа",
            'position': "Количество различных товаров",
            'full_price': "Общая сумма заказа",
            'status_pay': "Статусная оплата",
            'status': "Статус заказа",
            'discount': "Скидка",
            'created_at': "Время заказа"
        }, inplace=True)
        df3.rename(columns={
            'total_expenses': 'Общая стоимость расходов',
            'percentage_change': 'Стоимость расхода указана в процентах к предыдущему периоду'
        }, inplace=True)
        df4.rename(columns={
            'total_sales': 'Общее количество продаж',
            'percentage_change': 'Общее количество продаж в процентах по сравнению с предыдущим периодом',
        }, inplace=True)
        df5.rename(columns={
            'pay_type': 'Тип оплаты',
            'count': 'Количество',
            'total_amount': 'Общая сумма',
            'percentage': "В процентах"
        }, inplace=True)
        df6.rename(columns={
            'id': 'Номер закза',
            'status': 'Статус заказа',
            'order_type': 'Тип заказа',
            'status_pay': 'Статус оплаты',
            'position': 'Количество различных товаров',
            'full_price': 'Общая сумма заказа',
            'created_at': 'Время создание заказа',
            'discount': 'Скидка',
        }, inplace=True)
        df10.rename(columns={
            'category': 'Категория',
            'count': 'Количество продаж',
            'total_amount': 'Общая сумма',
            'percentage_quantity': 'В прочентах'
        }, inplace=True)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=Отчёт ({start_date} - {end_date}).xlsx'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df1.to_excel(writer, sheet_name='Статистика', index=False)
            df2.to_excel(writer, sheet_name='Заказы со скидкой', index=False)
            df3.to_excel(writer, sheet_name='Расходы', index=False)
            df4.to_excel(writer, sheet_name='Продажи', index=False)
            df5.to_excel(writer, sheet_name='Способы оплаты', index=False)
            df6.to_excel(writer, sheet_name='История заказов', index=False)
            df9.to_excel(writer, sheet_name='Отмененные заказы', index=False)
            df10.to_excel(writer, sheet_name='Популярные категории по товаров', index=False)

            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_name = column[0].column_letter
                    for cell in column:
                        try:
                            cell.alignment = Alignment(horizontal='center', vertical='center')
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except Exception as e:
                            print(f"Error processing cell: {e}")
                            pass
                    adjusted_width = (max_length + 10)
                    worksheet.column_dimensions[column_name].width = adjusted_width

        return response
