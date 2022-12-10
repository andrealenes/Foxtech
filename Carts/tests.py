from django.test import TestCase
from django.shortcuts import reverse

class CartViewTest(TestCase):

    def test_cart_is_empty(self):
        """
        Test para comprobar si se muestra correctamente un mensaje cuando el carrito de compras esta vacio.
        """
        # Realizar una peticion a la vista
        response = self.client.get(reverse('Carts:cart')) 
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tu carrito de compras esta vacio.')
        self.assertQuerysetEqual(response.context['carrito'].products_related(), [])