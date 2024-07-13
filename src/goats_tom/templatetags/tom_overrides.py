from django import template
from django.core.paginator import Paginator

register = template.Library()


@register.inclusion_tag(
    "tom_dataproducts/partials/saved_dataproduct_list_for_observation.html"
)
def goats_dataproduct_list_for_observation_saved(
    data_products, request, observation_record
):
    page = request.GET.get("page_saved")
    paginator = Paginator(data_products["saved"], 25)
    products_page = paginator.get_page(page)

    return {
        "products_page": products_page,
        "observation_record": observation_record,
    }
