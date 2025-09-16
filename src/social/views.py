from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from .models import Follow, Event

User = get_user_model()


@login_required
def user_search(request):
    """
    Поиск пользователей по имени/фамилии/отчеству/e-mail.
    Показываем кнопки Подписаться/Отписаться.
    """
    q = (request.GET.get("q") or "").strip()
    users = User.objects.none()
    if q:
        users = User.objects.filter(
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(middle_name__icontains=q) |
            Q(last_name__icontains=q)
        ).exclude(id=request.user.id)[:200]

    # кого я уже читаю — чтобы отрисовать кнопки
    following_ids = set(
        Follow.objects.filter(follower=request.user).values_list("followee_id", flat=True)
    )

    ctx = {
        "q": q,
        "users": users,
        "following_ids": following_ids,
    }
    return render(request, "social/search.html", ctx)


@login_required
def following(request):
    """
    Список моих подписок.
    """
    rows = (
        Follow.objects
        .filter(follower=request.user)
        .select_related("followee")
        .order_by("followee__first_name", "followee__last_name")
    )
    return render(request, "social/following.html", {"rows": rows})


@login_required
def follow(request, user_id: int):
    """
    Подписаться (ТОЛЬКО POST).
    """
    if request.method != "POST":
        messages.error(request, "Подписка доступна только через POST.")
        return redirect("social:search")

    target = get_object_or_404(User, id=user_id)
    if target.id == request.user.id:
        messages.error(request, "Нельзя подписаться на себя.")
        return redirect(request.META.get("HTTP_REFERER") or "social:search")

    Follow.objects.get_or_create(follower=request.user, followee=target)
    messages.success(request, f"Вы подписались на {target.email}.")
    return redirect(request.META.get("HTTP_REFERER") or "social:search")


@login_required
def unfollow(request, user_id: int):
    """
    Отписаться (ТОЛЬКО POST).
    """
    if request.method != "POST":
        messages.error(request, "Отписка доступна только через POST.")
        return redirect("social:search")

    target = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, followee=target).delete()
    messages.info(request, f"Вы отписались от {target.email}.")
    return redirect(request.META.get("HTTP_REFERER") or "social:search")

@login_required
def feed(request):
    """
    Лента событий:
    - ?filter=subs — только события от тех, на кого я подписан
    - ?q=строка — поиск по email или ФИО пользователя
    """
    q = (request.GET.get("q") or "").strip()
    flt = (request.GET.get("filter") or "").strip()

    followees = Follow.objects.filter(follower=request.user).values_list("followee_id", flat=True)

    if flt == "subs":
        user_ids = list(followees)
    else:
        user_ids = list(followees) + [request.user.id]

    qs = Event.objects.filter(user_id__in=user_ids).select_related("user")

    if q:
        qs = qs.filter(
            Q(user__email__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(user__middle_name__icontains=q)
        )

    events = qs.order_by("-created_at")[:100]

    return render(request, "social/feed.html", {"events": events})