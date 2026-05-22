from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User


#--------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------

# test para register
class RegisterTest(APITestCase):

    def test_user_registration(self):                   # un metodo de prueba

        url = reverse('register')                           # se obtiene la url del endpoint

        data = {                                            # datos de prueba  
            'email': 'test@gmail.com',
            'username': 'testuser',
            'password': 'TestPassword123',
            'password2': 'TestPassword123'
        }

        response = self.client.post(                      # se envia una peticion POST
            url,                                            # url del endpoint
            data,                                           # datos de prueba
            format='json'                                   # formato de los datos
        )

        self.assertEqual(                               # se verifica que el status code sea 201 created
            response.status_code,
            status.HTTP_201_CREATED                       # status code 201 created
        )

        self.assertEqual(                               # se verifica que exista un usuario
            User.objects.count(),
            1                                               # se espera que exista un usuario
        )




# test para login
class LoginTest(APITestCase):

    def setUp(self):                                    # se define un metodo setUp

        self.user = User.objects.create_user(         # se crea un usuario de prueba
            email='test@gmail.com',
            username='testuser',
            password='TestPassword123',
            is_verified=True
        )

    def test_user_login(self):                            # un metodo de prueba

        url = reverse('login')                            # se obtiene la url del endpoint

        data = {                                            # datos de prueba 
            'email': 'test@gmail.com',
            'password': 'TestPassword123'
        }

        response = self.client.post(                      # se envia una peticion POST
            url,                                            # url del endpoint
            data,                                           # datos de prueba
            format='json'                                   # formato de los datos
        )

        self.assertEqual(                               # se verifica que el status code sea 200 OK
            response.status_code,
            status.HTTP_200_OK                              # status code 200 OK
        )



# test para profile
class ProfileTest(APITestCase):

    def setUp(self):                                    # se define un metodo setUp

        self.user = User.objects.create_user(         # se crea un usuario de prueba
            email='test@gmail.com',
            username='testuser',
            password='TestPassword123'
        )

    def test_profile_access(self):                            # un metodo de prueba

        self.client.force_authenticate(                       # se autentica el cliente
            user=self.user                                      # usuario de prueba
        )

        url = reverse('profile')                              # se obtiene la url del endpoint

        response = self.client.get(url)                       # se envia una peticion GET

        self.assertEqual(                               # se verifica que el status code sea 200 OK
            response.status_code,
            status.HTTP_200_OK                              # status code 200 OK
        )