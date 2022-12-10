import pytest
from Products.models import Category

@pytest.mark.django_db
def test_create_category():
    category = Category.create(
        id_category = 2,
        name = "categoria 2",
        description = ""
    )
    assert category.id_category == 2

@pytest.mark.django_db
def test_create_category2():
    category = Category.create(
        id_category = 3,
        name = "categoria 3",
        description = ""
    )
    assert category.id_category == 3

@pytest.mark.django_db
def test_create_category3():
    category = Category.create(
        id_category = 4,
        name = "categoria 4",
        description = ""
    )
    assert category.id_category == 4