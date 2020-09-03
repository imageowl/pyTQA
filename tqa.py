#TQA : Module for Connecting to Total QA API

import requests
import json
import base64
import datetime
from dateutil import parser

client_id = ''
client_key = ''
base_url = 'https://tqa.imageowl.com/api/rest'
_oauth_ext = '/oauth'
_grant_type = 'client_credentials'
access_token = ''
token_duration = 0
token_type = ''
token_exp_time = ''
token_exp_margin = 0.9


def set_tqa_token():

        payload = {"client_id": client_id,
                   "client_secret": client_key,
                   "grant_type": _grant_type}

        request_url = base_url + _oauth_ext
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
                client_id = tqaCred['ClientID']

                global base_url
                base_url = tqaCred['BaseURL']

                global _oauth_ext
                _oauth_ext = tqaCred['OauthURL']

                key_bytes = base64.b64decode(tqaCred['APIKey'])
                global client_key
                client_key = key_bytes.decode('UTF-8')

                set_tqa_token()

def save_json_credentials(credential_file):
    #encode the key in base 64
    key_bytes = client_key.encode('UTF-8')
    key_bytes_b64 = base64.b64encode(key_bytes)
    base64_key = key_bytes_b64.decode('UTF-8')

    cred_info = {
        "ClientID":client_id,
        "APIKey": base64_key,
        "BaseURL": base_url,
        "OauthURL": _oauth_ext}

    tqa_cred_dict = {"TQACredentials":cred_info}

    json_out_file = open(credential_file, "w")
    json_out_file.write(json.dumps(tqa_cred_dict, indent=4, sort_keys=True))
    json_out_file.close()

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

def get_request(url_ext, raw_url = False):
        if raw_url:
            url = url_ext
        else:
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

def get_machine_id_from_str(find_machines):
        #if a simple str is passed then convert to a list
        if type(find_machines) == str:
                find_machines = [find_machines]

        machines = get_machines()
        machine_names = [m['name'] for m in machines['json']['machines']]
        machine_ids = [m['id'] for m in machines['json']['machines']]
        res = [i for i, val in enumerate(machine_names) if any(m in val for m in find_machines)]

        for i in res:
                # if string exactly matches a machine name
                if machine_names[i] == find_machines[0]:
                        return machine_ids[i]

        return [machine_ids[i] for i in res]


def get_equipment(equipment_id = -1):
        if equipment_id == -1:
                return get_request('/equipment')
        else:
                return get_request('/equipment/'+str(equipment_id))


def get_templates(template_id = -1):
        if template_id == -1:
                return get_request('/templates')
        else:
                templates = get_templates()
                template_ids = [t['id'] for t in templates['json']['templates']]
                for idx, t in enumerate(template_ids):
                        if t == template_id:
                                return templates['json']['templates'][idx]
                # get_request not working
                return get_request('/templates/'+str(template_id))


def get_schedules(schedule_id = -1):
        if schedule_id == -1:
                return get_request('/schedules')
        else:
                return get_request('/schedules/'+str(schedule_id))


def get_schedule_id_from_str(schedule_name, machine_idx = -1):
        if machine_idx == -1:
                raise Warning('Possible_Ambiguous_Results', 'Not specifying a machine id may result in'
                                                            'ambiguous results')

        # if a simple str is passed then convert to a list
        if type(schedule_name) == str:
                schedule_name = [schedule_name]

        # all schedules
        schedules = get_schedules()
        schedule_names = [s['name'] for s in schedules['json']['schedules']]
        schedule_ids = [s['id'] for s in schedules['json']['schedules']]
        res = [i for i, val in enumerate(schedule_names) if any(s in val for s in schedule_name)]
        # schedule ids of schedules with parameter name
        res_ids = [schedule_ids[i] for i in res]

        for idx, val in enumerate(schedules['json']['schedules']):
                machine = schedules['json']['schedules'][idx]['machineId']
                sched = schedules['json']['schedules'][idx]['id']
                if machine == machine_idx and sched in res_ids:
                        return sched
        return 'No schedules found with that id for specified machine id'


def get_custom_tests():
        return get_request('/custom-tests')


def get_baselines_and_tolerances(schedule_id):
        return get_request('/schedules/'+str(schedule_id)+'/tolerances')


def get_documents(document_id = -1):
        if document_id == -1:
                return get_request('/documents')
        else:
                return get_request('/documents/'+str(document_id))


def get_machine_energies():
        return get_request('/machine-energies')


def get_qa_settings(schedule_id):
        return get_request('/schedules/'+str(schedule_id)+'/qa-settings')


def get_schedule_variables(schedule_id):
        return get_request('/schedules/'+str(schedule_id)+'/variables')


def get_variable_id_from_string(var_name, schedule_idx):
        schedule_vars = get_schedule_variables(schedule_idx)

        if len(schedule_vars) == 0:
                return 'The list of variables is empty'

        # if a simple str is passed then convert to a list
        if type(var_name) == str:
                var_name = [var_name]

        variable_names = [v['name'] for v in schedule_vars['json']['variables']]
        variable_ids = [v['id'] for v in schedule_vars['json']['variables']]
        res = [i for i, val in enumerate(variable_names) if any(m in val for m in var_name)]
        return [variable_ids[i] for i in res]


def get_tests():
        return get_request('/tests')


def get_report_data(report_id):
        return get_request('/report-data/'+str(report_id))


def get_longitudinal_data(schedule_id, variable_ids = -1, date_start = -1, date_end = -1, date_format = -1):
        params = ''
        if variable_ids != -1:
                if isinstance(variable_ids, int) == 1:
                        params = params + 'variables=' + str(variable_ids)
                elif len(variable_ids) == 1:
                        params = params + 'variables=' + str(variable_ids[0])
                else:
                        params += 'variables='
                        for v in variable_ids:
                                params = params + str(v) + ','
                        params = params[:-1]

        if date_start != -1:
                if len(params) > 0:
                        params += '&'
                dStart = get_date_from_string(date_start, date_format)
                params = params + 'dateFrom=' + str(dStart)

        if date_end != -1:
                if len(params) > 0:
                        params += '&'
                dEnd = get_date_from_string(date_end, date_format)
                params = params + 'dateTo=' + str(dEnd)

        if len(params) > 0:
                params = '?' + params

        url_ext = '/schedules/'+str(schedule_id)+'/trends'+params

        return get_request(url_ext)


def get_date_from_string(date_str, date_format = -1):
        if date_format == -1:
                # no format specified
                dt = parser.parse(date_str)
        else:
                dt = datetime.datetime.strptime(date_str, date_format)

        dt = dt.strftime('%Y-%m-%dT%H:%M')
        return dt


def upload_test_results(schedule_id, variable_data, comment = -1, finalize = -1, date = -1, date_format = -1):
        # upload test results to a schedule
        dt_format, schedule_id, output_data = parse_upload_simple_data_input(schedule_id, variable_data, comment,
                                                                               finalize, date, date_format)
        output_dict = {'comment': comment, 'finalize': finalize, 'variables': output_data}
        headers = get_standard_headers()
        url_ext = ''.join(['/schedules/', str(schedule_id), '/add-results'])
        url_process = ''.join([base_url, url_ext])
        json_data = json.dumps(output_dict)
        return requests.post(url_process, headers=headers, data=json_data)


def parse_upload_simple_data_input(schedule_id, variable_data, comment, finalize, date, date_format):
        # if isinstance(variable_data, dict):  # then assume its a single measurement
        #         variable_data = [variable_data]

        if len(variable_data) == 0:
                variable_data = ['EMPTY']

        if date != -1:
                if date_format == -1:
                        # no format specified
                        dt = parser.parse(date)
                else:
                        dt = datetime.datetime.strptime(date, date_format)
                dt = dt.strftime('%Y-%m-%dT%H:%M')
        else:
                dt = ''

        for v in variable_data:

                # all must have at least id and value
                if 'id' not in v or 'value' not in v:
                        raise ValueError('TQAConnection:parse_upload_simple_data_input',
                                         'each element of the variable data must have id and value fields')

                # they MAY have a metaItems field in which case each metaitem must have an id and value
                if 'metaItems' in v:
                        if isinstance(v['metaItems'], dict):
                                # all must have at least id and value
                                if 'id' not in v['metaItems'] or 'value' not in v['metaItems']:
                                        raise ValueError('TQAConnection:parse_upload_simple_data_input',
                                                         'metaItem data must have id and value fields')
                                # if len(v['metaItems']) == 1:
                        elif isinstance(v['metaItems'], list):
                                for m in v['metaItems']:
                                        # all must have at least id and value
                                        if 'id' not in m or 'value' not in m:
                                                raise ValueError('TQAConnection:parse_upload_simple_data_input',
                                                                 'metaItem data must have id and value fields')
        return dt, schedule_id, variable_data


def upload_analysis_file(schedule_id,file_path):
        headers = get_standard_headers()
        #remove the content-type for this call
        del headers['content-type']
        url_ext = ''.join(['/schedules/',str(schedule_id),'/upload-images'])
        url = ''.join([base_url,url_ext])
        files = [
            ('file',(file_path,open(file_path,'rb'),'application/octet-stream'))
            ]
        return requests.post( url, headers=headers, data = {}, files = files)

def start_processing(schedule_id):
        headers = get_standard_headers()
        url_ext = ''.join(['/schedules/',str(schedule_id),'/start-processing'])
        url_process = ''.join([base_url,url_ext])
        return requests.post( url_process, headers=headers, data = {})

def finalize_report(schedule_id):
        headers = get_standard_headers()
        url_ext = ''.join(['/schedules/',str(schedule_id),'/finalize-results'])
        url_process = ''.join([base_url,url_ext])
        return requests.post( url_process, headers=headers, data = {})

def get_upload_status(schedule_id):
        return get_request(''.join(['/schedules/',str(schedule_id),'/upload-images']))


def get_reports(**kwargs):
        param_keys = ['machine','site','schedule','status','toleranceStatus',
        'deviceType','frequency']

        param = {}
        for p in param_keys:
                param[p] = -1

        param.update(**kwargs)

        #build the filter
        filter = ''

        for p in param_keys:

                if not param[p] == -1:
                        if len(filter) > 0:
                                filter += '&'
                        filter += "{}={}".format(p,str(param[p]))


        if len(filter) > 0: filter = '?{}'.format(filter)

        url_ext = "/reports{}".format(filter)

        #get the initial report response
        reports = [];
        rep_response = get_request(url_ext)
        rep_json = rep_response["json"]

        if "reports" in rep_json.keys() and len(rep_json["reports"]) > 0:
                reports.extend(rep_json["reports"])
                #now see if there are further pages
                while ("_metadata" in rep_json.keys() and
                "Links" in rep_json["_metadata"].keys() and
                "next" in rep_json["_metadata"]["Links"].keys() and
                len(rep_json["_metadata"]["Links"]["next"]) > 0):
                        print(rep_json["_metadata"]["Links"]["next"])
                        rep_response = get_request(rep_json["_metadata"]["Links"]["next"],True)
                        rep_json = rep_response["json"]
                        if "reports" in rep_json.keys() and len(rep_json["reports"]) > 0:
                                reports.extend(rep_json["reports"])


        return reports

