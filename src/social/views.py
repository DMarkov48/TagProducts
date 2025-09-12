from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Follow, Event

User = get_user_model()

@login_required
def user_search(request):
    q = request.GET.get("q", "").strip()
    users = User.objects.none()
    if q:
        users = User.objects.filter(
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(middle_name__icontains=q)
        ).exclude(id=request.user.id).order_by("email")[:50]
    # отмечаем, на кого уже подписан
    following_ids = set(Follow.objects.filter(follower=request.user).values_list("followee_id", flat=True))
    return render(request, "social/search.html", {"q": q, "users": users, "following_ids": following_ids})


@login_required
def follow(request, user_id):
    if request.method != "POST":
        return redirect("social:search")
    target = get_object_or_404(User, id=user_id)
    if target.id == request.user.id:
        messages.info(request, "Нельзя подписаться на себя.")
        return redirect("social:search")
    Follow.objects.get_or_create(follower=request.user, followee=target)
    messages.success(request, f"Вы подписались на {target.email}.")
    next_url = request.META.get("HTTP_REFERER") or reverse("social:search")
    return redirect(next_url)


@login_required
def unfollow(request, user_id):
    if request.method != "POST":
        return redirect("social:search")
    target = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, followee=target).delete()
    messages.info(request, f"Вы отписались от {target.email}.")
    next_url = request.META.get("HTTP_REFERER") or reverse("social:search")
    return redirect(next_url)


@login_required
def following_list(request):
    rows = (Follow.objects
            .filter(follower=request.user)
            .select_related("followee")
            .order_by("followee__email"))
    return render(request, "social/following.html", {"rows": rows})


@login_required
def feed(request):
    # события моих подписок + мои собственные
    followees = Follow.objects.filter(follower=request.user).values_list("followee_id", flat=True)
    user_ids = list(followees) + [request.user.id]
    events = (Event.objects
              .filter(user_id__in=user_ids)
              .select_related("user")
              .order_by("-created_at")[:100])
    return render(request, "social/feed.html", {"events": events})