import pytest
from django.core.paginator import Paginator
from goats_tom.templatetags import bootstrap_pagination


@pytest.fixture()
def page():
    # Create a mock Page object
    paginator = Paginator(range(100), 10)  # 100 items, 10 per page
    page = paginator.page(1)
    return page


def test_bootstrap_pagination_normal(page):
    # Normal case
    context = bootstrap_pagination(page)
    assert context["start_index"] == 1
    assert context["end_index"] == 10
    assert context["total_count"] == 100


def test_bootstrap_pagination_middle_page():
    # Middle page case
    paginator = Paginator(range(100), 10)
    page = paginator.page(5)
    context = bootstrap_pagination(page)
    assert context["start_index"] == 41
    assert context["end_index"] == 50
    assert context["total_count"] == 100


def test_bootstrap_pagination_last_page():
    # Last page case
    paginator = Paginator(range(95), 10)  # 95 items, 10 per page
    page = paginator.page(10)
    context = bootstrap_pagination(page)
    assert context["start_index"] == 91
    assert context["end_index"] == 95
    assert context["total_count"] == 95


def test_bootstrap_pagination_single_item():
    # Single item case
    paginator = Paginator(range(1), 1)  # 1 item, 1 per page
    page = paginator.page(1)
    context = bootstrap_pagination(page)
    assert context["start_index"] == 1
    assert context["end_index"] == 1
    assert context["total_count"] == 1


def test_bootstrap_pagination_no_items():
    # No items case
    paginator = Paginator([], 10)  # 0 items, 10 per page
    page = paginator.page(1)
    context = bootstrap_pagination(page)
    assert context["start_index"] == 0
    assert context["end_index"] == 0
    assert context["total_count"] == 0
