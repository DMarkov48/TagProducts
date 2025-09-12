from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Product, Category
import datetime
from django.db import models

def product_list(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "").strip()

    qs = Product.objects.all().select_related()
    if q:
        qs = qs.filter(models.Q(name__icontains=q) | models.Q(kind__icontains=q))
    if cat:
        qs = qs.filter(categories__slug=cat)

    qs = qs.distinct().order_by("name", "kind")

    paginator = Paginator(qs, 12)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    categories = Category.objects.order_by("name")
    today = datetime.date.today()

    ctx = {
        "page_obj": page_obj,
        "q": q,
        "categories": categories,
        "current_cat": cat,
        "today": today,           # ← добавили
    }
    return render(request, "products/list.html", ctx)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    today = datetime.date.today()
    return render(request, "products/detail.html", {"product": product, "today": today})