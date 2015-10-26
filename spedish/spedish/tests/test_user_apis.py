'''
API tests for the User model

Created on Sep 8, 2015

@author: jyxu
'''

from copy import deepcopy
import json

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase 

from spedish.models import UserProfile


class UserAPITests(APITestCase):
    
    # This allow long data structures to be diffed when an error occurs
    maxDiff = None
    
    testUser = 'testAccountABC'
    testPass = 'testAccountPass'
    testEmail = 'jyxu@jamesyxu.com'
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
    extraAddress1 = {
                    'line_one': '2nd street',
                    'line_two': 'LINE2',
                    'city': 'SF',
                    'state': 'CA',
                    'zip_code': '94587'
    }
    extraAddress2 = {
                    'line_one': 'Blah ave',
                    'line_two': 'line2',
                    'city': 'LA',
                    'state': 'CA',
                    'zip_code': '90024'
    }
    
    isSetup = False
    
    def setUp(self):
        if not self.isSetup:    
            self._testCreateUser()
            self.isSetup = True
            
    def tearDown(self):
        self._logout()
    
    def _login(self):
        url = reverse('user-auth-api')
        
        response = self.client.post(url, {'username': self.testUser, 'password': self.testPass})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check we are now logged in 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def _logout(self):
        url = reverse('user-auth-api')
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that we are currently not logged in
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
                
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
    
    def _testGetUserInfo(self):
        url = reverse('user-profile-api')
        
        # Return data does not contain password and has id field for address
        returnData = deepcopy(self.data)
        returnData['user'].pop('password')
        
        # Bad request, not logged in
        self._logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        self._login()
        
        # Get the user info
        response = self.client.get(url)
        # We don't care about the insert IDs
        responseObj = json.loads(str(response.content, encoding='utf-8'))
        del responseObj['address'][0]['id']
        del responseObj['address'][1]['id']
        self.assertJSONEqual(json.dumps(responseObj), returnData)
        
        return json.loads(str(response.content, encoding='utf-8'))
    
    def testUpdateUserInfo(self):
        self._login()
        
        url = reverse('user-profile-api')
        
        # Since the ids etc are not deterministic, we will utilize GetUserInfo
        # to get the currently available user information
        userInfo = self._testGetUserInfo()
        
        putData = deepcopy(userInfo)
        
        # Replace address entry for 1 and setup id for 1 and 2
        slotId = putData['address'][0]['id']
        putData['address'][0] = deepcopy(self.extraAddress1)
        putData['address'][0]['id'] = slotId
        
        # Return data does not contain password and has id field for address
        returnData = deepcopy(userInfo)
        returnData['address'][0] = deepcopy(self.extraAddress1)
        returnData['address'][0]['id'] = slotId
        
        response = self.client.put(url, putData, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(url, data={'username': self.testUser})
        self.assertJSONEqual(str(response.content, encoding='utf-8'), returnData)

        # Add 2 additional addresses (extraAddress1 and 2)
        putData['address'].append(deepcopy(self.extraAddress1))
        putData['address'].append(deepcopy(self.extraAddress2))
        putData['address'][2]['id'] = 0
        putData['address'][3]['id'] = 0
        
        returnData['address'].append(deepcopy(self.extraAddress1))
        returnData['address'].append(deepcopy(self.extraAddress2))
        # The expected IDs are slotId (which is entry 0) + 2 for the first one
        # since we have 2 entries already in entry 0 and 1
        returnData['address'][2]['id'] = slotId + 2
        returnData['address'][3]['id'] = slotId + 3
        
        response = self.client.put(url, putData, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(url, data={'username': self.testUser})
        self.assertJSONEqual(str(response.content, encoding='utf-8'), returnData)
        
        # Delete address with id 2
        for i in range(0,4):
            putData['address'][i]['id'] = returnData['address'][i]['id']
            
        del putData['address'][1]
        del returnData['address'][1]
        
        response = self.client.put(url, putData, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(url, data={'username': self.testUser})
        self.assertJSONEqual(str(response.content, encoding='utf-8'), returnData)

    def testFBLogin(self):
        url = reverse('fb-user-auth-api')
        
        self._logout()
        
        # Use a bad token
        badToken = 'This token will never work'
        response = self.client.post(url, {'token': badToken})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Now ask for a good token
        goodToken = input("Input FB access token: ")
        response = self.client.post(url, {'token': goodToken})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify we are reporting logged in
        response = self.client.get(reverse('user-auth-api'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def testLoginLogout(self):
        '''
        This test also covers the Login Status API
        '''
        url = reverse('user-auth-api')
        
        self._logout()
        
        # Attempt failed login
        response = self.client.post(url, {'username': self.testUser, 'password': 'abcd'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        self._login()
        
        self._logout()
