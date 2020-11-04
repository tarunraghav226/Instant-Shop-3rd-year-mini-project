from user.models import Products
from django.db.models import Q

def search(search_text):

    search_text = search_text.split(" ")

    all_products = set()

    for text in search_text:
        all_products.add(Products.objects.filter(
            Q(name__icontains = text) |
            Q(description__icontains = text) |
            Q(price__icontains = text) |
            Q(features__icontains = text) |
            Q(months_of_product_used__icontains = text)
        )[0])
    return all_products