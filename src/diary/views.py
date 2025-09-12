import datetime
import calendar
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from .models import DiaryEntry
from .services import ensure_challenge_for, get_progress
from django.db.models import Count

@login_required
def join_challenge(request):
    ensure_challenge_for(request.user)
    messages.success(request, "Вы вступили в проект! Удачи на пути к 400 продуктам.")
    return redirect("diary:index")

@login_required
def add_entry(request):
    """Добавление записи в дневник (через POST). Ожидает product_id и опционально date."""
    if request.method != "POST":
        return redirect("diary:index")

    product_id = request.POST.get("product_id")
    date_str = request.POST.get("date")  # YYYY-MM-DD
    amount = request.POST.get("amount_grams")
    note = request.POST.get("note", "").strip()

    if not product_id:
        messages.error(request, "Не указан продукт.")
        return redirect("diary:index")

    try:
        date = datetime.date.fromisoformat(date_str) if date_str else datetime.date.today()
    except ValueError:
        messages.error(request, "Неверная дата.")
        return redirect("diary:index")

    ensure_challenge_for(request.user)

    try:
        DiaryEntry.objects.create(
            user=request.user,
            product_id=product_id,
            date=date,
            amount_grams=int(amount) if amount else None,
            note=note
        )
        messages.success(request, f"Добавлено на {date.isoformat()}.")
    except IntegrityError:
        messages.info(request, "Этот продукт уже отмечен на выбранную дату.")

    next_url = request.META.get("HTTP_REFERER") or reverse("diary:index")
    return redirect(next_url)

@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)
    entry.delete()
    messages.info(request, "Запись удалена.")
    return redirect("diary:index")

@login_required
def diary_view(request):
    """Главная страница дневника: прогресс и список записей за выбранную дату."""
    # дата из GET, по умолчанию — сегодня
    date_str = request.GET.get("date")
    try:
        current_date = datetime.date.fromisoformat(date_str) if date_str else datetime.date.today()
    except ValueError:
        current_date = datetime.date.today()

    unique_count, target, days_elapsed, days_total = get_progress(request.user)

    entries = (DiaryEntry.objects
               .filter(user=request.user, date=current_date)
               .select_related("product")
               .order_by("product__name", "product__kind"))

    ctx = {
        "current_date": current_date,
        "entries": entries,
        "unique_count": unique_count,
        "target": target,
        "days_elapsed": days_elapsed,
        "days_total": days_total,
    }
    return render(request, "diary/index.html", ctx)

@login_required
def month_view(request):
    """
    Календарь на месяц с количеством записей по дням.
    GET-параметры:
      - year: YYYY
      - month: 1..12
    По умолчанию — текущий месяц.
    """
    today = datetime.date.today()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    # Границы месяца
    first_day = datetime.date(year, month, 1)
    last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])

    # Собираем количество записей по дням
    counts = (
        DiaryEntry.objects
        .filter(user=request.user, date__gte=first_day, date__lte=last_day)
        .values("date")
        .annotate(n=Count("id"))
    )
    # Превратим в словарь: {date: n}
    per_day = {row["date"]: row["n"] for row in counts}

    # Сетка календаря: список недель, в каждой 7 дат (или None для пустых мест)
    cal = calendar.Calendar(firstweekday=0)
    weeks = []
    week = []
    for d in cal.itermonthdates(year, month):
        # itermonthdates выдаёт и хвосты соседних месяцев — их помечаем None
        if d.month != month:
            week.append(None)
        else:
            week.append(d)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)

    unique_count, target, days_elapsed, days_total = get_progress(request.user)

    # Даты для переключателей
    prev_month = (first_day - datetime.timedelta(days=1)).replace(day=1)
    next_month = (last_day + datetime.timedelta(days=1)).replace(day=1)

    ctx = {
        "year": year,
        "month": month,
        "weeks": weeks,
        "per_day": per_day,
        "unique_count": unique_count,
        "target": target,
        "days_elapsed": days_elapsed,
        "days_total": days_total,
        "prev_year": prev_month.year,
        "prev_month": prev_month.month,
        "next_year": next_month.year,
        "next_month": next_month.month,
        "today": today,
    }
    return render(request, "diary/month.html", ctx)