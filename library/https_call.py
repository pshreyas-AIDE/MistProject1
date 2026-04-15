import json
import urllib3
# pip uninstall urllib3
# pip install 'urllib3<2.0'
import os
import sys
import requests
import string
import time
import copy
from datetime import datetime




'''
URL = 'https://api.mistsys.com/api/v1/orgs/a85ecd8b-95e9-4ce7-88e0-356b27e2486f/networks'
ENV = 'staging'
ORG_ID = 'a85ecd8b-95e9-4ce7-88e0-356b27e2486f'
'''

class HTTP_Calls:
    def __init__(self,AWS_STAGING_TOKEN):
        self.session = requests.Session()
        self.header = {'Content-Type': 'application/json', 'Authorization': 'Token ' + AWS_STAGING_TOKEN}

    def get_call(self,url):
        #print(" Starting to Execute the Get Request for URL : ",url)
        return_response=self.session.get(url=url, headers=self.header)
        response = return_response.json()
        status = return_response.status_code
        #print('\tStatus: {}'.format(status))
        #print('\tResponse: {}'.format(response))
        if(status != 200):
            print('Failed to GET API')
        else:
            print('Successfully GET API')
            return response


    def put_call(self,url,payload):
        print(" Starting to Execute the Put Request for URL : ",url)
        return_response=self.session.put(url=url, json=payload, headers=self.header)
        response = return_response.json()
        status = return_response.status_code
        print('\tStatus: {}'.format(status))
        print('\tResponse: {}'.format(response))
        if(status != 200):
            print('Failed to GET API')
        else:
            print('Successfully GET API')
            return response

    def post_call(self,url,payload):
        print(" Starting to Execute the Post Request for URL : ",url)
        return_response=self.session.post(url=url, json=payload, headers=self.header)
        response = return_response.json()
        status = return_response.status_code
        print('\tStatus: {}'.format(status))
        print('\tResponse: {}'.format(response))
        if(status != 200):
            print('Failed to GET API')
        else:
            print('Successfully GET API')
            return response

    def head_call(self,url):
        print(" Starting to Execute the Head Request for URL : ",url)
        return_response=self.session.head(url=url, headers=self.header)
        response = return_response.json()
        status = return_response.status_code
        print('\tStatus: {}'.format(status))
        print('\tResponse: {}'.format(response))
        if(status != 200):
            print('Failed to GET API')
        else:
            print('Successfully GET API')
            return response

    def delete_call(self,url):
        print(" Starting to Execute the Delete Request for URL : ",url)
        return_response=self.session.delete(url=url, headers=self.header)
        response = return_response.json()
        status = return_response.status_code
        print('\tStatus: {}'.format(status))
        print('\tResponse: {}'.format(response))
        if(status != 200):
            print('Failed to GET API')
        else:
            print('Successfully GET API')
            return response

    def close_session(self):
        self.session.close()
