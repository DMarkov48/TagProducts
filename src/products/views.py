from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request):
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "").strip()

    qs = Product.objects.all().select_related()
    if q:
        qs = qs.filter(name__icontains=q)
    if cat:
        qs = qs.filter(categories__slug=cat)

    qs = qs.distinct().order_by("name")

    paginator = Paginator(qs, 12)  # 12 карточек на страницу
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    categories = Category.objects.order_by("name")
    ctx = {"page_obj": page_obj, "q": q, "categories": categories, "current_cat": cat}
    return render(request, "products/list.html", ctx)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "products/detail.html", {"product": product})