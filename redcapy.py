"""
    Redcapy.py interacts with more commonly used Redcap API methods.
"""

import pycurl
import json

from io import BytesIO
from urllib.parse import urlencode
from bs4 import BeautifulSoup

__version__ = '0.9.1'
__author__ = 'William Santo'
__date__ = 'July 2017'


class Redcapy:
    def __init__(self, api_token, redcap_url):
        self.redcap_token = api_token
        self.redcap_url = redcap_url

    def __core_api_code__(self, post_data, opt_post_data_kvpairs=None):
        """
            Common code elements to access Redcap API

            :param post_data:  String that had been formatted as a json object using json.dumps()
            :param opt_post_data_kvpairs:  Key value pairs to override POST data defaults.  Other
                    internal methods provide key checks for post fields; however, no such checks
                    are included if this override is used here.

            :return: JSON/XML/str containing either the expected output or an error message, depending
                    on the call.  Please check your Redcap documentation for any given method for
                    further details.

            WARNING: TODO: Code has only been tested to return JSON responses from server.  Additional
                work may be required to accommodate specification of xml or csv responses.
        """

        if opt_post_data_kvpairs is None:
            opt_post_data_kvpairs = {}

        assert isinstance(post_data, dict), "{} passed to core_api_code method \
            expected a dict but received a {} object".format(post_data, type(post_data))
        
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.redcap_url)

        if opt_post_data_kvpairs is not None:
            for key, value in opt_post_data_kvpairs.items():
                post_data[key] = value

        post_fields = urlencode(post_data)
        c.setopt(c.POSTFIELDS, post_fields)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        return_value = str(buffer.getvalue(), 'utf-8')  # convert byte to str object
        buffer.close()

        try:
            return json.loads(return_value)
        except:  # delete method on error returns xml
            return_soup = BeautifulSoup(str(return_value), 'xml')
            return return_soup.hash.error.get_text()
        else:
            print('return_value was not loaded as a JSON nor XML object:', return_value)
            return return_value

    def __api_error_handler__(self, error_message):
        # TODO
        print('From __api_error_handler__ (this output may be expected in a unit test):', error_message)

    def export_events(self, **kwargs):
        """
            Export events from Redcap

            WARNING: Not all optional arguments have been tested.  Defaults are set in post_data.

            Note that the format for returned data is the format field, not the returnFormat field.

            Example of returned content:
                [{"event_name":"Baseline","arm_num":"2","day_offset":"0","offset_min":"0",
                "offset_max":"0", "unique_event_name":"baseline_arm_2","custom_event_label":null}]

        :param kwargs:
            token: {your token}
            content: event
            format: json/csv/xml
            arms: a comma separated string of arm numbers that you wish to pull events for (Default = all arms)
            returnFormat: json/csv/xml

        :return: JSON object containing either the expected output or an error message from __core_api_code__ method
        """

        post_data = {
            'token': self.redcap_token,
            'content': 'event',
            'format': 'json',
            'returnFormat': 'json'
        }
        
        if kwargs is not None:
            for key, value in kwargs.items():
                if key in ['token',
                           'content',
                           'format',
                           'arms',
                           'returnFormat']:         
                    post_data[key] = kwargs[key]    
                else:
                    print('{} is not a valid key'.format(key))          

        return self.__core_api_code__(post_data=post_data)

    def export_data_dictionary(self, **kwargs):
        """
            Export the data definitions.

            Any changes to the POST data will be passed entirely to core_api_code method to
                replace the default POST options.
            Note that the format for returned data is the format field, not the returnFormat field.

            :param kwargs: Available options (check post_data for defaults)
                token: {your token}
                content: metadata
                format: json/csv/xml

                OPTIONAL
                --------
                fields: string (Comma separated if multiple)
                forms: string (Comma separated if multiple)
                returnFormat: json/csv/xml

            :return: JSON object containing either the expected output or an error message from
                    __core_api_code__ method
        """

        post_data = {
            'token': self.redcap_token,
            'content': 'metadata',
            'format': 'json',
            'returnFormat': 'json'
        }
        
        if kwargs is not None:
            for key, value in kwargs.items():
                if key in ['token',
                           'content',
                           'format',
                           'fields',
                           'forms',
                           'returnFormat']:         
                    post_data[key] = kwargs[key]    
                else:
                    print('{} is not a valid key'.format(key))            

        return self.__core_api_code__(post_data=post_data)

    def export_records(self, **kwargs):
        """
            Export records (study data) from Redcap.

            WARNING: Not all optional arguments have been tested.  Defaults are set in post_data.

            Any changes to the POST data will be passed entirely to core_api_code method to
                replace the default POST options.
            Note that the format for returned data is the format field, not the returnFormat field.

            Example usage:
                from redcap.redcapy import Redcapy
                redcap_token = os.environ['your project token string']
                redcap_url = os.environ['redcap server url']
                rc = Redcapy(api_token=redcap_token, redcap_url=redcap_url)
                data_export = rc.export_records(rawOrLabel='label',
                                    fields='consent_date, randomization_id, record_id')

            :param kwargs: Available options
                token: {your token}
                content: record
                format: json/csv/xml
                type: flat/eav
                rawOrLabel: raw/label
                rawOrLabelHeaders: raw/label
                exportCheckboxLabel: false/true
                exportSurveyFields: false/true
                exportDataAccessGroups: false/true
                returnFormat: json/csv/xml
                fields: string (Comma separated as a single string, not list, if multiple)
                forms: string (Comma separated as a single string, not list, if multiple)
                events: string (Comma separated as a single string, not list, if multiple)

            :return JSON object containing either the expected output or an error message from
                    __core_api_code__ method
        """

        post_data = {
            'token': self.redcap_token,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'rawOrLabel': 'raw',
            'rawOrLabelHeaders': 'raw',
            'exportCheckboxLabel': 'false',
            'exportSurveyFields': 'false',
            'exportDataAccessGroups': 'false',
            'returnFormat': 'json'
        }

        if kwargs is not None:
            for key, value in kwargs.items():
                if key in ['fields', 
                           'forms', 
                           'events', 
                           'token',
                           'content',
                           'format',
                           'type',
                           'rawOrLabel',
                           'rawOrLabelHeaders',
                           'exportCheckboxLabel',
                           'exportSurveyFields',
                           'exportDataAccessGroups',
                           'returnFormat']:         
                    post_data[key] = kwargs[key]    
                else:
                    print('{} is not a valid key'.format(key))                    
            
        return self.__core_api_code__(post_data=post_data)

    def import_records(self, data_to_upload, **kwargs):
        """
            Upload records into Redcap.
            Note the post_data format field should match the data of the data field
            JSON data should be passed in as a string, formatted to dump into JSON format, or a list that can
                be dumped into JSON.
            When passed as a jaon formatted string, the json should be enclosed with [].  If not present, then this
                will add [].
            So the tested json data_to_upload format is a dict wrapped by json.dumps

            WARNING: Not all optional arguments have been tested.  Defaults are set in post_data.


            :param data_to_upload: json str
            :param kwargs:  Available options (check post_data for defaults)
                token: {your token}
                content: record
                format: json/csv/xml
                type: flat/eav
                overwriteBehavior: normal/overwrite
                data: {your data}
                dateFormat: MDY, DMY, YMD: NOTE: The default format is Y-M-D (with dashes), while MDY and DMY
                        values should always be formatted as M/D/Y or D/M/Y (with slashes), respectively.
                returnContent: count/ids/nothing
                returnFormat: json/csv/xml

            :return: JSON object containing either the expected output or an error message from__core_api_code__ method
                Server response contains an 'error' key if an error occurs.
                Otherwise returns a count of successful imports by default.
        """

        post_data = {
            'token': self.redcap_token,
            'content': 'record',
            'format': 'json',
            'type': 'flat',
            'overwriteBehavior': 'normal',
            'data': data_to_upload,
            'dateFormat': 'YMD',
            'returnContent': 'count',
            'returnFormat': 'json'
        }

        if kwargs is not None:
            for key, value in kwargs.items():
                if key in ['token',
                           'content',
                           'format',
                           'type',
                           'overwriteBehavior',
                           'data',
                           'dateFormat',
                           'returnContent',
                           'returnFormat']:         
                    post_data[key] = kwargs[key]    
                else:
                    print('{} is not a valid key'.format(key))
                    
        if post_data['format'] == 'json':
            if type(data_to_upload) == str:
                if data_to_upload[:1] != '[':
                    try:
                        json.loads(data_to_upload)
                        data_to_upload = json.dumps([json.loads(data_to_upload)])
                        post_data['data'] = data_to_upload
                    except Exception as e:
                        print('Please check if the data_to_upload field is formatted properly for conversion to JSON\n')
        else:
            # TODO
            pass

        return self.__core_api_code__(post_data=post_data)

    def delete_record(self, id_to_delete, **kwargs):
        """
            Delete a single record from Redcap.
            This has been reduced from a more general multiple record delete, which requires additional
                keys in the format of record[0], record[1], record[2], ...
            To delete multiple records, iterate a list of IDs in a loop

            WARNING: Not all optional arguments have been tested.  Defaults are set in post_data.

            :param id_to_delete: str
            :param kwargs: Available options (check post_data for defaults)
                token: {your token}
                content: record
                format: json/csv/xml
                records[0]: id string
                arm: optional (longitudinal study may have multiple arms, so specify a single arm, else delete from all)

            :return: The number of records deleted
        """

        post_data = {
            'token': self.redcap_token,
            'action': 'delete',
            'content': 'record',
            'records[0]': id_to_delete
        }
        
        if kwargs is not None:
            for key, value in kwargs.items():
                if key in ['token',
                           'content',
                           'records[0]',
                           'arm']:         
                    post_data[key] = kwargs[key]    
                else:
                    print('{} is not a valid key'.format(key))        

        return self.__core_api_code__(post_data=post_data)

    def delete_form(self, id, field, event, repeat_instance, **kwargs):
        """
            Delete a single field from a form in Redcap.
            This has been reduced from a more general multiple record delete, which requires additional
                keys in the format of record[0], record[1], record[2], ...

            WARNING: Not all optional arguments have been tested.  Defaults are set in post_data.

            :param id: str
            :param field: str
            :param event: str
            :param repeat_instance: str
            :param kwargs: Available options (check post_data for defaults)
                token: {your token}
                content: record
                format: json/csv/xml
                records[0]: id string
                arm: optional (longitudinal study may have multiple arms, so specify a single arm, else delete from all)

            :return: The number of records deleted
        """

        post_data = {
            'token': self.redcap_token,
            'content': 'file',
            'action': 'delete',
            'record': id,
            'field': field,
            'event': event,
            'repeat_instance': repeat_instance
        }

        if kwargs is not None:
            for key, value in kwargs.items():
                if key in ['token',
                           'content',
                           'action',
                           'records[0]',
                           'field',
                           'event',
                           'repeat_instance'
                           ]:
                    post_data[key] = kwargs[key]
                else:
                    print('{} is not a valid key'.format(key))

        return self.__core_api_code__(post_data=post_data)