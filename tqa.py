#TQA : Module for Connecting to Total QA API

import requests
import json
import base64
import datetime

clientID = '';
clientKey = '';
baseURL = 'https://tqa.imageowl.com/api/rest'
oauthExt = '/oauth'
grantType = 'client_credentials'
accessToken = ''
tokenDuration = 0;
tokenType = '';
tokenExpirationTime = ''
tokenExpirationMargin = 0.9

def setTQAToken():
    
        payload = {"client_id": clientID,
                   "client_secret": clientKey,
                   "grant_type": grantType}

        requestURL = baseURL + oauthExt
        r = requests.post(requestURL ,data = payload)

        j = r.json()
        global accessToken
        accessToken = j['access_token']
        
        global tokenDuration
        tokenDuration = j['expires_in']
        
        global tokenType
        tokenType = j['token_type']

        global tokenExpirationTime
        tokenExpirationTime = datetime.datetime.now()+datetime.timedelta(seconds=tokenDuration)

    

def loadCredentialsFromJSON(credentialFile):
        with open(credentialFile) as credFile:
                cred = json.load(credFile)
                tqaCred = cred['TQACredentials']
                
                global clientID
                clientID = tqaCred['ClientID']

                global baseURL
                baseURL = tqaCred['BaseURL']

                global oauthExt
                oauthExt = tqaCred['OauthURL']

                keyBytes = base64.b64decode(tqaCred['APIKey'])
                global clientKey
                clientKey = keyBytes.decode('UTF-8')

                setTQAToken()
                

def getStandardHeaders():
        if accessToken == '':
                setTQAToken()
        else:
                closeTimeDelta = datetime.timedelta(seconds =(1-tokenExpirationMargin)*tokenDuration)
                if datetime.datetime.now() > tokenExpirationTime - closeTimeDelta:
                        setTQAToken()

        bearerToken = 'Bearer ' + accessToken
        headers = {
            'authorization': bearerToken,
            'content-type': "application/json",
            'accept': "application/json",
        }
        return headers

def getRequest(urlExt):
        url = baseURL + urlExt
        response = requests.request("GET",url,headers = getStandardHeaders())
        
        return {'json':response.json(),
                'status':response.status_code,
                'raw':response}

def getSites():
        return getRequest('/sites')

def getUsers(userID = -1):
        if userID == -1:
                return getRequest('/users')
        else:
                return getRequest('/users/'+str(userID))

def getMachines(active = -1,site = -1, deviceType = -1):
        #build the filter
        filter = ''
        if not active == -1:
                filter = filter + 'active=' +str(active)

        if not site == -1:
                if len(filter) > 0: filter += '&'
                filter = filter + 'site=' + str(site)

        if not deviceType == -1:
                if len(filter) > 0: filter += '&'
                filter = filter + 'deviceType=' + str(deviceType)

        if len(filter) > 0: filter = '?' + filter

        urlExt = '/machines'+filter
        
        return getRequest(urlExt)

def getReportData(reportId):
        return getRequest('/report-data/'+str(reportId))

        





        
                





        
    
    
