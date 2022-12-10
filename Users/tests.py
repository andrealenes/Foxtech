from django.test import TestCase
from .models import City

# Create your tests here.
class CityModelTest(TestCase):

    def test_created_city(self):
        """
        Test unitario para verificar que se esta creando correctamente las instancias del modelo City.
        """
        city = City.objects.create(description = 'Ciudad ejemplo', zip_code = '321345')
        self.assertIs(city.id_city, 1)

    def test_length_zip_code(self):
        """
        Test unitario para verificar que cuando se crea una instancia del modelo city el campo zip_code tenga maximo 6 caracteres.
        """
        city = City.objects.create(description = 'Ciudad ejemplo', zip_code = '321345')
        self.assertIs(city.length_zip_code(), True)