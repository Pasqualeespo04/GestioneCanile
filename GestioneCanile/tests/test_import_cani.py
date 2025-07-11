from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from GestioneCanile.models import Canile, Cane
import io
import csv

class ImportCaniTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        
        # Create a test shelter
        self.canile = Canile.objects.create(
            nome='Canile Test',
            indirizzo='Via Test 123',
            citta='Test City',
            telefono='1234567890',
            email='test@canile.it',
            capacita_massima=100
        )
        
    def test_import_cani(self):
        # Login the user
        self.client.login(username='testuser', password='testpassword')
        
        # Create a test CSV file
        csv_data = io.StringIO()
        writer = csv.writer(csv_data)
        writer.writerow(['Nome', 'Razza', 'Data di nascita', 'Sesso', 'Peso', 'Microchip', 'Sterilizzato', 'ID Canile'])
        writer.writerow(['Rex', 'Pastore Tedesco', '2020-05-15', 'M', '30.5', '123456789012345', 'Si', self.canile.id])
        writer.writerow(['Luna', 'Labrador', '2019-10-20', 'F', '25.2', '987654321098765', 'No', self.canile.id])
        
        # Reset the pointer to the beginning of the file
        csv_data.seek(0)
        
        # Create a file-like object for the POST request
        csv_file = io.BytesIO(csv_data.getvalue().encode('utf-8'))
        csv_file.name = 'test_dogs.csv'
        
        # Make the POST request to import the dogs
        response = self.client.post(
            reverse('import_cani'),
            {'csv_file': csv_file},
            format='multipart'
        )
        
        # Check that the response is a redirect or success
        self.assertEqual(response.status_code, 200)
        
        # Check that the dogs were created
        self.assertEqual(Cane.objects.count(), 2)
        
        # Check the details of the imported dogs
        rex = Cane.objects.get(nome='Rex')
        self.assertEqual(rex.razza, 'Pastore Tedesco')
        self.assertEqual(rex.sesso, 'M')
        self.assertEqual(float(rex.peso), 30.5)
        self.assertEqual(rex.microchip, '123456789012345')
        self.assertTrue(rex.sterilizzato)
        
        luna = Cane.objects.get(nome='Luna')
        self.assertEqual(luna.razza, 'Labrador')
        self.assertEqual(luna.sesso, 'F')
        self.assertEqual(float(luna.peso), 25.2)
        self.assertEqual(luna.microchip, '987654321098765')
        self.assertFalse(luna.sterilizzato)