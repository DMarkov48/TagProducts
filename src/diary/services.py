import datetime
from django.db.models import Count
from .models import Challenge, DiaryEntry

def ensure_challenge_for(user):
    """Создать челлендж, если его ещё нет."""
    ch = getattr(user, "challenge", None)
    if ch is None:
        start = datetime.date.today()
        ch = Challenge.objects.create(user=user, start_date=start, end_date=start + datetime.timedelta(days=365))
    return ch

def get_progress(user):
    """Вернёт (unique_count, target, days_elapsed, days_total) по активному челленджу"""
    ch = getattr(user, "challenge", None)
    if not ch:
        return (0, 400, 0, 365)

    # Сколько уникальных продуктов за окно челленджа
    qs = (DiaryEntry.objects
          .filter(user=user, date__gte=ch.start_date, date__lte=ch.end_date)
          .values("product")  # уникальные продукт-объекты (учитывают сорт)
          .distinct())
    unique_count = qs.count()

    # Сколько дней прошло с начала (не больше 365)
    today = datetime.date.today()
    days_elapsed = max(0, (min(today, ch.end_date) - ch.start_date).days + 1)
    days_total = (ch.end_date - ch.start_date).days + 1

    return (unique_count, ch.target_unique, days_elapsed, days_total)
