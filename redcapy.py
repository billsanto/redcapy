"""
    Redcapy.py interacts with more commonly used Redcap 8.1.3 API endpoints.
"""

import pycurl
import json
import re

from io import BytesIO
from urllib.parse import urlencode
from bs4 import BeautifulSoup

__version__ = '0.9.5'
__author__ = 'William Santo'
__date__ = 'June 2018'


class Redcapy:
    def __init__(self, api_token, redcap_url, verify_ssl=False):
        self.redcap_token = api_token
        self.redcap_url = redcap_url
        self.verify_ssl = verify_ssl

    def __core_api_code(self, post_data, opt_post_data_kvpairs=None):
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

        if self.verify_ssl:
            c.setopt(c.SSL_VERIFYPEER, 1)
            c.setopt(c.SSL_VERIFYHOST, 2)

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

        # export_survey_link returns a URL as a str, so try this first
        if return_value and isinstance(return_value, str):
            if self.__find_url(return_value) == return_value:
                return return_value

        try:
            return json.loads(return_value)
        except Exception as e:  # delete method on error returns xml
            try:
                return_soup = BeautifulSoup(str(return_value), 'xml')
                return return_soup.hash.error.get_text()
            except Exception as e2:
                print('Error: Data returned from Redcap was not a JSON nor XML object. Data: ', return_value)
                return return_value

    def __api_error_handler(self, error_message):
        # TODO
        print('From __api_error_handler__ (this output may be expected in a unit test):', error_message)

    @staticmethod
    def __find_url(str_to_parse):
        """
            Ref: https://www.geeksforgeeks.org/python-check-url-string/
        :param string:
        :return: str, URL of the first URL found in the supplied str argument
        """

        url_list = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]| [! * \(\),] | (?: %[0-9a-fA-F][0-9a-fA-F]))+',
                              str_to_parse)
        return url_list[0] if len(url_list) > 0 else ''

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

        return self.__core_api_code(post_data=post_data)

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

        return self.__core_api_code(post_data=post_data)

    def export_survey_link(self, instrument, event, record, **kwargs):
        """
            Export a survey link to a single survey based on required arguments.

            Any changes to the POST data will be passed entirely to core_api_code method to
                replace the default POST options.
            Note that the format for returned data is the format field, not the returnFormat field.

            :param kwargs: Available options (check post_data for defaults)
                token: {your instance token}
                content: metadata
                format: json/csv/xml
                returnFormat: json/csv/xml

            :param instrument: Redcap instrument name
            :param event: Redcap event name
            :param record: record_id

            :return: JSON object containing either the expected output or an error message from
                    __core_api_code__ method
        """

        post_data = {
            'token': self.redcap_token,
            'content': 'surveyLink',
            'format': 'json',
            'instrument': instrument,
            'event': event,
            'record': record,
            'returnFormat': 'json',
        }

        if kwargs is not None:
            for key, value in kwargs.items():
                if key in ['token',
                           'content',
                           'format',
                           'returnFormat']:
                    post_data[key] = kwargs[key]
                else:
                    print('{} is not a valid key'.format(key))

        return self.__core_api_code(post_data=post_data)

    def export_survey_participants(self, instrument, event, **kwargs):
        """
            Export full list of surveys for a combination of instrument and event

            Any changes to the POST data will be passed entirely to core_api_code method to
                replace the default POST options.
            Note that the format for returned data is the format field, not the returnFormat field.

            :param kwargs: Available options (check post_data for defaults)
                token: {your instance token}
                content: metadata
                format: json/csv/xml
                returnFormat: json/csv/xml

            :param instrument: Redcap instrument name
            :param event: Redcap event name

            :return: JSON object containing either the expected output or an error message from
                    __core_api_code__ method
        """

        post_data = {
            'token': self.redcap_token,
            'content': 'participantList',
            'format': 'json',
            'instrument': instrument,
            'event': event,
            'returnFormat': 'json',
        }

        if kwargs is not None:
            for key, value in kwargs.items():
                if key in ['token',
                           'content',
                           'format',
                           'returnFormat']:
                    post_data[key] = kwargs[key]
                else:
                    print('{} is not a valid key'.format(key))

        return self.__core_api_code(post_data=post_data)

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
            
        return self.__core_api_code(post_data=post_data)

    def import_records(self, data_to_upload, **kwargs):
        """
            Upload single records into Redcap.  Bulk imports have not been tested.
            Note the post_data format field should match the data of the data field
            JSON data should be passed in as a string, formatted to dump into JSON format, or a list that can
                be dumped into JSON.
            When passed as a jaon formatted string, the json should be enclosed with [].  If not present, then this
                will add [].
            So the tested json data_to_upload format is a dict wrapped by json.dumps

            Example USAGE:

                If using a pandas Dataframe, for example, at minimum it needs to have the following column names:
                  record_id
                  redcap_event_name

                For a repeating instrument, it should also have
                 redcap_repeat_instrument (form name)
                 redcap_repeat_instance (int, one-based, not zero-based)

                And of course the name of any other valid Redcap fields
                To update the form completion status, the column name is typically the form name (underscores for blanks),
                followed by _complete.  The name can be verified by exporting from the API Playground in Redcap.
                Then use data values of 0 or 1 or 2 for various completion states.  Form completion status is optional.

                df_to_upload = pd.DataFrame('Your Data')
                for i in range(len(df_to_upload)):
                    record_to_upload = df_to_upload.iloc[i].to_json(orient='columns')
                    import_return = rc.import_records(data_to_upload=record_to_upload)

                It is your responsibility to check the response above and react to errors for each record.  Despite the
                small performance overhead of single vs. bulk record imports, this makes it easy to manage exceptions
                and retries.


            WARNING: Not all optional arguments have been tested.  Defaults are set in post_data.


            :param data_to_upload: json str
            :param kwargs:  Available options (check post_data for defaults)
                token: {your token}
                content: record
                format: json/csv/xml
                type: flat/eav
                overwriteBehavior: normal/overwrite (Use overwrite to overwrite non-null fields with empty strings)
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

        return self.__core_api_code(post_data=post_data)

    def delete_record(self, id_to_delete, **kwargs):
        """
            Delete a single record from Redcap.
            This has been reduced from a more general multiple record delete, which requires additional
                keys in the format of record[0], record[1], record[2], ...
            To delete multiple records, iterate a list of IDs in a loop, which is acceptable for small scale deletes

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

        return self.__core_api_code(post_data=post_data)

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

        return self.__core_api_code(post_data=post_data)

    def import_file(self, record_id, field, event, filename, repeat_instance=None, **kwargs):
        """
            Upload a file into Redcap.

            Example Usage:
                from redcap.redcapy import Redcapy
                redcap_token = os.environ['your project token string']
                redcap_url = os.environ['redcap server url']
                rc = Redcapy(api_token=redcap_token, redcap_url=redcap_url)
                html_full_path = os.path.abspath('my_filename.html')
                import_response = rc.import_file(event='data_import_arm_1',
                                                 field='redcap_field_name',
                                                 filename=html_full_path,
                                                 record_id='1',
                                                 repeat_instance='2',
                                                )
                # import_response is null if upload is successful

            :param data_to_upload: json str
            :param record_id: record_id
            :param field: field name of field in Redcap
            :param event: event name in Redcap
            :param filename: file name (on local system) to import
            # Note that unlike a data import, this next param is not called redcap_repeat_instance
            :param repeat_instance: optional
            :param kwargs:  Available options (check post_data for defaults)
                token: {your token}

            :return: None if successful, else potentially useful debugging info is returned
        """

        post_data = {
            'token': self.redcap_token,
            'content': 'file',
            'format': 'json',
            'action': 'import',
            'record': record_id,
            'field': field,
            'event': event,
            'returnFormat': 'json',
            'file': (pycurl.FORM_FILE, filename),
        }

        if repeat_instance:
            post_data['repeat_instance'] = str(repeat_instance)

        if kwargs is not None:
            for key, value in kwargs.items():
                if key in ['token',
                           'content',
                           'format',
                           'action',
                           'record',
                           'field',
                           'event',
                           'returnContent',
                           'file',
                           ]:
                    post_data[key] = str(kwargs[key])
                else:
                    print('{} is not a valid key'.format(key))

        else:
            # TODO
            pass

        # Normally this would be processed by the core method, but it is customized here due to the null response
        # that the server returns after a proper data import.
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.redcap_url)
        c.setopt(c.HTTPPOST, list(post_data.items()))
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        c.close()
        return_value = str(buffer.getvalue(), 'utf-8')  # convert byte to str object
        buffer.close()

        if len(return_value) > 0:
            try:
                return json.loads(return_value)
            except Exception as e:  # delete method on error returns xml
                try:
                    return_soup = BeautifulSoup(str(return_value), 'xml')
                    return return_soup.hash.error.get_text()
                except Exception as e2:
                    print('Error: Data returned from Redcap was not a JSON nor XML object. Data: ', return_value)
                    return return_value
        else:
            return True

