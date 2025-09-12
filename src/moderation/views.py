import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ProposalCreateForm, ProposalModerateForm
from .models import ProductProposal
from products.models import Product, Category

def is_moderator(user):
    return user.is_authenticated and (user.is_staff or user.groups.filter(name="moderators").exists())

# --- Пользователь: отправка заявки ---
@login_required
def proposal_submit(request):
    if request.method == "POST":
        form = ProposalCreateForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.status = "pending"
            obj.save()
            messages.success(request, "Заявка отправлена на модерацию.")
            return redirect("products:list")
    else:
        form = ProposalCreateForm()
    return render(request, "moderation/submit.html", {"form": form})

# --- Модератор: список заявок ---
@user_passes_test(is_moderator)
def moderation_list(request):
    status = request.GET.get("status", "pending")
    qs = ProductProposal.objects.all().order_by("-created_at")
    if status in {"pending", "approved", "rejected"}:
        qs = qs.filter(status=status)
    return render(request, "moderation/list.html", {"rows": qs, "status": status})

# --- Модератор: карточка заявки ---
@user_passes_test(is_moderator)
def moderation_detail(request, pk: int):
    prop = get_object_or_404(ProductProposal, pk=pk)
    if request.method == "POST":
        form = ProposalModerateForm(request.POST, instance=prop)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные заявки обновлены.")
            return redirect("moderation:detail", pk=prop.pk)
    else:
        form = ProposalModerateForm(instance=prop)
    return render(request, "moderation/detail.html", {"obj": prop, "form": form})

# утилита: найти/создать категории из текстового поля
def _get_categories_from_text(categories_text: str):
    names = [x.strip() for x in (categories_text or "").split(",") if x.strip()]
    cats = []
    for name in names:
        slug = name.lower().replace(" ", "-")
        cat, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name})
        cats.append(cat)
    return cats

# --- Модератор: одобрить → создать Product ---
@user_passes_test(is_moderator)
def moderation_approve(request, pk: int):
    prop = get_object_or_404(ProductProposal, pk=pk)
    if prop.status == "approved":
        messages.info(request, "Заявка уже одобрена.")
        return redirect("moderation:detail", pk=pk)

    # создаём/обновляем продукт (уникальность по (name, kind))
    prod, created = Product.objects.get_or_create(
        name=prop.name.strip(),
        kind=prop.kind.strip(),
        defaults={
            "group": prop.group or "other",
            "kcal": prop.kcal or 0,
            "proteins": prop.proteins or 0,
            "fats": prop.fats or 0,
            "carbs": prop.carbs or 0,
        }
    )
    # фото (если было приложено и у продукта пусто)
    if prop.photo and not prod.photo:
        prod.photo = prop.photo
        prod.save(update_fields=["photo"])

    # категории
    cats = _get_categories_from_text(prop.categories_text)
    if cats:
        prod.categories.add(*cats)

    # обновляем статусы
    prop.status = "approved"
    prop.reviewer = request.user
    prop.reviewed_at = timezone.now()
    prop.save(update_fields=["status", "reviewer", "reviewed_at"])

    messages.success(request, f"Одобрено. Продукт {'создан' if created else 'обновлён'}: {prod}")
    return redirect("moderation:detail", pk=pk)

# --- Модератор: отклонить ---
@user_passes_test(is_moderator)
def moderation_reject(request, pk: int):
    prop = get_object_or_404(ProductProposal, pk=pk)
    if request.method == "POST":
        reason = (request.POST.get("reason") or "").strip()
        prop.status = "rejected"
        prop.reviewer = request.user
        prop.reviewed_at = timezone.now()
        if reason:
            # добавим причину в комментарий
            prop.comment = (prop.comment + "\n\n[Причина отклонения]\n" + reason).strip()
        prop.save(update_fields=["status", "reviewer", "reviewed_at", "comment"])
        messages.info(request, "Заявка отклонена.")
        return redirect("moderation:detail", pk=pk)
    # простая форма с текстовым полем
    return render(request, "moderation/reject.html", {"obj": prop})