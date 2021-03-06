# Redcapy

----
### Overview

This code contains several basic methods to access a Redcap 7/8/9 server instance using the Python API.  The Redcap API offers a broader array of features not implemented here.  It may be possible to add any other Redcap endpoint not available here by adapting the Python 2 examples in the API Playground and this library.

Only JSON output has been implemented (no XML/CSV to date). Note that for some endpoints Redcap may produce XML. Read the Redcapy method of interest for details.

Currently, the following features are known to work in Redcap 9.0.
- import records
- import file
- delete file
- export records
- delete record
- export data dictionary
- export survey link
- export events

The following worked in 7.4.7 but have not been tested recently.

- delete form

### Examples
#### Set up
```python
from redcap.redcapy import Redcapy
import os

# Using environment variables for tokens, or you cut/paste your own directly into code (not recommended)
redcap_token = os.environ['your project token string']
redcap_url = os.environ['redcap server url']

# Create a Redcap instance
rc = Redcapy(api_token=redcap_token, redcap_url=redcap_url)

# Examine attributes of instance: 
print(rc)  # Example: Redcapy instance connected to https://redcap.ucsf.edu/api/ with token 9A3***************************10

# If needed, create a second Redcap instance, which would be useful for merging data from different projects
redcap_token2 = os.environ['your other project token string']
rc2 = Redcapy(api_token=redcap_token2, redcap_url=redcap_url)
```

#### Export Records from Redcap

Note that if you specify an invalid field name, it will be ignored.
```python
from pprint import print

# Full export. Projects with a lot of data (events, fields, ids) will take noticeably longer to download. 
data_export = rc.export_records(rawOrLabel='label')
pprint(data_export)  # If successful, data_export is a list of dicts

# Export select fields from all events
data_export = rc.export_records(rawOrLabel='label', fields='consent_date, record_id')
pprint(data_export) 

# Export all data for only record id 1, 2, and 3 from all events
data_export = rc.export_records(rawOrLabel='label', records='1,2,3')
pprint(data_export)

# Export all data for only record id 1, 2, and 3 from the baseline event only. Use the raw, not labeled event.
data_export = rc.export_records(rawOrLabel='label', records='1,2,3', events='baseline_arm_1')
pprint(data_export)

# Export data from a single form for only record id 1, 2, and 3 from the baseline event.
# Use the raw, not labeled event and form name. Separate multiple criteria with a comma.
data_export = rc.export_records(rawOrLabel='label', records='1,2,3', 
                                events='baseline_arm_1', forms='randomization_and_group_form')
pprint(data_export)

```

#### Import Records to Redcap

Note when importing data, be sure to specify record_id and redcap_event_name.
Also, if the project contains repeating instruments, also be sure to add redcap_repeat_instrument and redcap_repeat_instance to each record. Failure to do so may result in unintended overwriting of data. It is strongly advisable to practice importing in a copy of your production project and checking the outcome before updating a production project. 

Note that upon a successful import, the count value in the response is a reference to the number of record IDs affected, not the actual number of records (ID/event combinations). This matters when checking the response from a bulk import, in contrast to a record by record import.

Also, a record imported into Redcap, if identical to all the existing values in that record, will return a positive API response, but that will not be evident from checking the log in the Redcap UI, which will show no evidence of the import. In the UI, only fields which have changed will be listed. So if data for 5 record_ids are imported into Redcap, and all the values are identical to existing data in Redcap, the API response count = 5, but there will be no entries in the Redcap log. 
```python
import pandas as pd

# Sample data
data=[
    {'record_id': '1', 'redcap_event_name': 'baseline_arm_1', 'consent_date': '2019-01-01'},
    {'record_id': '2', 'redcap_event_name': 'baseline_arm_1', 'consent_date': '2019-01-02'}
    ]

# Import data, one record at a time from a pandas DataFrame
df_to_upload = pd.DataFrame(data)

for i, row in df_to_upload.iterrows():
    record_to_upload = row.to_json(orient='columns')
    import_return = rc.import_records(data_to_upload=record_to_upload)


# Import data, one record at a time, using a list of dicts instead
import json

for d in data:
    record_to_upload = json.dumps(d)
    import_return = rc.import_records(data_to_upload=record_to_upload)


# Default behavior does not overwrite existing Redcap data with blank field values. 
# Use overwriteBehavior='overwrite' to do so for each field being imported. 
# Note that there are legitimate use cases for removing existing data, in which case you must use the overwrite option.
# For example, say we want to reset the consent dates above to blanks for testing purposes
for d in data:
    d['consent_date'] = ''
    record_to_upload = json.dumps(d)
    import_return = rc.import_records(data_to_upload=record_to_upload, overwriteBehavior='overwrite')


# Add tracking to the import
records_imported_attempted_count = 0
records_imported_count = 0

for d in data:
    record_to_upload = json.dumps(d)
    records_imported_attempted_count += 1
    import_return = rc.import_records(data_to_upload=record_to_upload)

    if 'count' in import_return and import_return['count'] == 1:
        records_imported_count += 1

print('Successfully imported {} of {} attempts'.format(records_imported_count, records_imported_attempted_count))


# Bulk import of list of dicts (more than one record at a time)
rc.import_records(data_to_upload=json.dumps(data))
# returns {'count': 2} if successful
```
#### Import File to Redcap

Unlike the records import, file import does not use the repeating instrument parameter, and the instance parameter name is different.
```python
# Import a file into a repeating instrument, an apparently undocumented feature
import_response = rc.import_file(event='data_import_arm_1',
                                 field='redcap_field_name',
                                 filename='full_path_filename',
                                 record_id='1',
                                 repeat_instance='2',
                                )
```
#### Delete File from Redcap
```python
# Delete the file imported above
delete_response = rc.delete_file(event='data_import_arm_1',
                                 field='redcap_field_name',
                                 record_id='1',
                                 repeat_instance='2',
                                )
# Or, add an action argument of 'delete' to the import_file method
delete_response = rc.import_file(event='data_import_arm_1',
                                 field='redcap_field_name',
                                 record_id='1',
                                 repeat_instance='2',
                                 action='delete',
                                )
```
#### Delete Entire Record from Redcap
```python
# This method is convenient for development/testing, but use very carefully, if at all, for production.
# Example: Delete all data for Record ID 30
rc.delete_record(30)

# Example of Bulk delete: delete Record IDs 1-14.
[rc.delete_record(id) for id in range(1, 15)]
```
#### Export Survey Link from Redcap
```python

# Example, Retrieve a single URL for the 2 Month survey for a given combination of instrument/event/record_id
instrument_name = 'your raw instrument name'  # e.g., '2_month_survey'
event_name = 'your raw event name'  # e.g., '2_month_arm_1'
record_id = '101'
url = rc.export_survey_link(instrument=instrument_name, event=event_name, record=record_id)

print(url)
# https://redcap.ucsf.edu/surveys/?s=abcdefghij
```

#### Export Data Dictionary from Redcap
```python
dd = rc.export_data_dictionary()  # returns a list of dicts, where each dict contains metadata for every field in the project
dd_df = pd.DataFrame.from_records(dd)  # convert to a pandas DataFrame
```

#### Export Records and Data Dictionary from Redcap using customized number of attempts

By default, all export methods will conduct multiple attempts as needed to retrieve data.  This is useful because a Redcap server may reject a valid export request for various reasons.  For example, a common error encountered when performing multiple exports with large amounts of data is: 'Connection broken: OSError("(54, \'ECONNRESET\')",)'.

You can change the defaults by specifying a limit to the number of reattempts and/or the number of seconds to wait between attempts.  Defaults may vary by export method and may change in the future, so specify an appropriate limit for your situation.
```python
export_fields = ['record_id', 'redcap_event_name', 'consent_date', 'randomization_date']

rc_visit_raw = export_records(limit=3, wait_secs=5, fields=export_fields)  # up to 3 attempts, waiting 5 secs before each reattempt
rc_visit_label = export_records(limit=5, wait_secs=10, fields=export_fields)  # up to 5 attempts, waiting 10 secs before each reattempt
rc_visit_dd = export_data_dictionary(limit=10, wait_secs=5)  # up to 10 attempts, waiting 5 secs before reattempt

if (not rc_visit_raw) or (not rc_visit_label) or (not rc_visit_dd):
    msg = 'Error: Failed to export data from Redcap.'
    raise ValueError(msg)
```



