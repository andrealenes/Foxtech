import pytest
from Products.models import Category
from django.test import TestCase
from .models import Product
from .models import UnitOfMeasure
from django.shortcuts import reverse

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

class ProductDetailViewTest(TestCase):

    def test_product_is_not_active(self):
        """
        Test unitario para comprobar que solo se podra ver el detalle de los productos que esten activos.
        """
        product = Product.objects.create(
            name = 'Producto ejemplo',
            image = '',
            unit_of_measure = UnitOfMeasure.objects.create(name = 'Kilogramo'),
            state = False
        )

        url = reverse('Products:product', args = (product.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)