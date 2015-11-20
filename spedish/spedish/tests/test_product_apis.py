'''
Created on Nov 17, 2015

@author: xcshen
'''

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from copy import deepcopy
import urllib
import tempfile
import os

class ProductAPITest(APITestCase):
    
    def setUp(self):
        self.tempDir = tempfile.gettempdir()
        urllib.request.urlretrieve("http://www.beginwithinnutrition.com/wp-content/uploads/2014/02/sqaure1.jpg", os.path.join(self.tempDir, "Test_Image.jpg"))
        img = open(os.path.join(self.tempDir, "Test_Image.jpg"), 'rb')
        uploaded = SimpleUploadedFile(img.name, img.read())
        self.data = {'name': 'Test', 'product_image': uploaded}
    
    def tearDown(self):        
        os.remove(os.path.join(self.tempDir, "Test_Image.jpg"))
        del self.data, self.tempDir
    
    def test_create_product(self):
        """
        Ensure we can create a new product.
        """
        
        url = reverse('product-profile-api')
        
        # Create a product
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Bad request: missing product image
        badData = deepcopy(self.data)
        badData.pop('product_image')
        response = self.client.post(url, badData)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
