#TQA : Module for Connecting to Total QA API

import requests
import json
import base64
import datetime

client_id = ''
client_key = ''
base_url = 'https://tqa.imageowl.com/api/rest'
oauth_ext = '/oauth'
grant_type = 'client_credentials'
access_token = ''
token_duration = 0
token_type = ''
token_exp_time = ''
token_exp_margin = 0.9

def set_tqa_token():
    
        payload = {"client_id": client_id,
                   "client_secret": client_key,
                   "grant_type": grant_type}

        request_url = base_url + oauth_ext
        r = requests.post(request_url ,data = payload)

        j = r.json()
        global access_token
        access_token = j['access_token']
        
        global token_duration
        token_duration = j['expires_in']
        
        global token_type
        token_type = j['token_type']

        global token_exp_time
        token_exp_time = datetime.datetime.now()+datetime.timedelta(seconds=token_duration)

    

def load_json_credentials(credential_file):
        with open(credential_file) as cred_file:
                cred = json.load(cred_file)
                tqaCred = cred['TQACredentials']
                
                global client_id
                client_id = tqaCred['client_id']

                global base_url
                base_url = tqaCred['base_url']

                global oauth_ext
                oauth_ext = tqaCred['OauthURL']

                key_bytes = base64.b64decode(tqaCred['APIKey'])
                global client_key
                client_key = key_bytes.decode('UTF-8')

                set_tqa_token()
                

def get_standard_headers():
        if access_token == '':
                set_tqa_token()
        else:
                close_time_delta = datetime.timedelta(seconds =(1-token_exp_margin)*token_duration)
                if datetime.datetime.now() > token_exp_time - close_time_delta:
                        set_tqa_token()

        bearer_token = 'Bearer ' + access_token
        headers = {
            'authorization': bearer_token,
            'content-type': "application/json",
            'accept': "application/json",
        }
        return headers

def get_request(url_ext):
        url = base_url + url_ext
        response = requests.request("GET",url,headers = get_standard_headers())
        
        return {'json':response.json(),
                'status':response.status_code,
                'raw':response}

def get_sites():
        return get_request('/sites')

def get_users(user_id = -1):
        if user_id == -1:
                return get_request('/users')
        else:
                return get_request('/users/'+str(user_id))

def get_machines(active = -1,site = -1, device_type = -1):
        #build the filter
        filter = ''
        if not active == -1:
                filter = filter + 'active=' +str(active)

        if not site == -1:
                if len(filter) > 0: filter += '&'
                filter = filter + 'site=' + str(site)

        if not device_type == -1:
                if len(filter) > 0: filter += '&'
                filter = filter + 'device_type=' + str(device_type)

        if len(filter) > 0: filter = '?' + filter

        url_ext = '/machines'+filter
        
        return get_request(url_ext)

def get_report_data(report_id):
        return get_request('/report-data/'+str(report_id))

        





        
                





        
    
    
