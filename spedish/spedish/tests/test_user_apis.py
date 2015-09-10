'''
API tests for the User model

Created on Sep 8, 2015

@author: jyxu
'''

from copy import deepcopy
import json

from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase 

from spedish.models import UserProfile


class UserAPITests(APITestCase):
    
    testUser = 'testAccountABC'
    testPass = 'testAccountPass'
    testEmail = 'test@test.com'
    data = {
            'user': {
                'username': testUser,
                'password': testPass,
                'first_name': testUser,
                'last_name': testPass,
                'email': testEmail,
            },
            'isSeller': True,
            'address': [
                {
                    'line_one': '11731 SE 65th St',
                    'line_two': '',
                    'city': 'Bellevue',
                    'state': 'WA',
                    'zip_code': '98006'
                },
                {
                    'line_one': '925 Weyburn Pl',
                    'line_two': '',
                    'city': 'Los Angeles',
                    'state': 'CA',
                    'zip_code': '90024'
                }
            ]
    }
    
    isSetup = False
    
    def setUp(self):
        if not self.isSetup:
            self._testCreateUser()
            self.isSetup = True
            
            APITestCase.setUp(self)
    
    def _testCreateUser(self):
        # delete the test user if it exists
        try:
            userProfile = UserProfile.objects.get(user__username = self.testUser)
            if userProfile:
                userProfile.delete()

        except ObjectDoesNotExist:
            # We expect this error
            pass
        except:
            self.fail('Unknown exception')
        
        url = reverse('user-profile-api')
        badData = deepcopy(self.data)
        badData['user'].pop('username')
        
        # Create bad data: missing username
        response = self.client.post(url, badData, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Complete the data
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def testGetUserInfo(self):
        url = reverse('user-profile-api')
        
        # Return data does not contain password
        returnData = deepcopy(self.data)
        returnData['user'].pop('password')
        
        # Bad request, no username
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Bad request, user not found
        response = self.client.get(url, data={'username': 'blah'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        response = self.client.get(url, data={'username': self.testUser})
        self.assertJSONEqual(str(response.content, encoding='utf-8'), returnData)

    def testLoginLogout(self):
        '''
        This test also covers the Login Status API
        '''
        url = reverse('user-auth-api')
        
        # Call logout once to make sure we are logged out
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that we are currently not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Attempt failed login
        response = self.client.post(url, {'username': self.testUser, 'password': 'abcd'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Attempt good login
        response = self.client.post(url, {'username': self.testUser, 'password': self.testPass})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check we are now logged in 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Call logout once to make sure we are logged out
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that we are currently not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
