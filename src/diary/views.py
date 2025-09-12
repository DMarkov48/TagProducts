import calendar
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import DiaryEntry
from .services import ensure_challenge_for, get_progress
from products.models import Product
from social.models import Event


@login_required
def join_challenge(request):
    """
    Создаёт челлендж пользователю, если его ещё нет,
    и возвращает на страницу дневника.
    """
    ensure_challenge_for(request.user)
    messages.success(request, "Вы вступили в проект! Удачи на пути к 400 продуктам.")
    return redirect("diary:index")


@login_required
def add_entry(request):
    """
    Добавление записи в дневник (через POST).
    Ожидает: product_id (обязательно), date (YYYY-MM-DD, опционально),
    amount_grams (опционально), note (опционально).
    При успехе создаёт событие для ленты (Event).
    """
    if request.method != "POST":
        return redirect("diary:index")

    product_id = request.POST.get("product_id")
    date_str = request.POST.get("date")
    amount = request.POST.get("amount_grams")
    note = (request.POST.get("note") or "").strip()

    if not product_id:
        messages.error(request, "Не указан продукт.")
        return redirect("diary:index")

    try:
        date = datetime.date.fromisoformat(date_str) if date_str else datetime.date.today()
    except ValueError:
        messages.error(request, "Неверная дата.")
        return redirect("diary:index")

    # гарантируем наличие челленджа
    ensure_challenge_for(request.user)

    try:
        entry = DiaryEntry.objects.create(
            user=request.user,
            product_id=product_id,
            date=date,
            amount_grams=int(amount) if amount else None,
            note=note,
        )
        # создаём событие ленты
        p = Product.objects.get(id=product_id)
        Event.objects.create(
            user=request.user,
            type="entry_created",
            payload={
                "product_id": p.id,
                "product_name": p.name,
                "kind": p.kind,
                "date": date.isoformat(),
            },
        )
        messages.success(request, f"Добавлено на {date.isoformat()}.")
    except IntegrityError:
        # запись такого же продукта на ту же дату уже есть
        messages.info(request, "Этот продукт уже отмечен на выбранную дату.")

    next_url = request.META.get("HTTP_REFERER") or reverse("diary:index")
    return redirect(next_url)


@login_required
def delete_entry(request, entry_id: int):
    """
    Удаляет запись из дневника текущего пользователя.
    """
    entry = get_object_or_404(DiaryEntry, id=entry_id, user=request.user)
    entry.delete()
    messages.info(request, "Запись удалена.")
    return redirect("diary:index")


@login_required
def diary_view(request):
    """
    Главная страница дневника: показывает прогресс и список записей за выбранную дату.
    GET ?date=YYYY-MM-DD — опционально.
    """
    date_str = request.GET.get("date")
    try:
        current_date = datetime.date.fromisoformat(date_str) if date_str else datetime.date.today()
    except ValueError:
        current_date = datetime.date.today()

    unique_count, target, days_elapsed, days_total = get_progress(request.user)

    entries = (
        DiaryEntry.objects
        .filter(user=request.user, date=current_date)
        .select_related("product")
        .order_by("product__name", "product__kind")
    )

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

    # границы месяца
    first_day = datetime.date(year, month, 1)
    last_day = datetime.date(year, month, calendar.monthrange(year, month)[1])

    # количество записей по дням
    counts = (
        DiaryEntry.objects
        .filter(user=request.user, date__gte=first_day, date__lte=last_day)
        .values("date")
        .annotate(n=Count("id"))
    )
    per_day = {row["date"]: row["n"] for row in counts}

    # сетка календаря (недели по 7 дней, пустые слоты = None)
    cal = calendar.Calendar(firstweekday=0)  # 0 = понедельник
    weeks = []
    week = []
    for d in cal.itermonthdates(year, month):
        week.append(d if d.month == month else None)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)

    unique_count, target, days_elapsed, days_total = get_progress(request.user)

    # даты для переключателей
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