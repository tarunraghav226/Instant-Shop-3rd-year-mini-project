from user.models import Products
from django.db.models import Q

def search(search_text):

    search_text = search_text.split(" ")

    all_products = set()

    for text in search_text:
        searched_product = Products.objects.filter(
            Q(name__icontains = text) |
            Q(description__icontains = text) |
            Q(price__icontains = text) |
            Q(features__icontains = text) |
            Q(months_of_product_used__icontains = text)
        )
        if len(searched_product) > 0:
            all_products.add(searched_product[0])
    return all_products