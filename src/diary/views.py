import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from .models import DiaryEntry
from .services import ensure_challenge_for, get_progress

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