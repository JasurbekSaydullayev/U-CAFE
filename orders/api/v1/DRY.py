from django.utils import timezone
from datetime import timedelta


def dry(request):
    start_date = request.query_params.get('start_date', (timezone.now() - timedelta(days=30)).date())
    end_date = request.query_params.get('end_date', timezone.now().date())
    if isinstance(start_date, str):
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

    start_date = timezone.make_aware(timezone.datetime.combine(start_date, timezone.datetime.min.time()))
    end_date = timezone.make_aware(timezone.datetime.combine(end_date, timezone.datetime.max.time()))
    return start_date, end_date
