# Redcapy

----
### Overview

This code contains several basic methods to access a Redcap 7/8 server instance using the Python API.  The Redcap API offers a broader array of features not implemented here.  It may be possible to add any other Redcap endpoint not available here by adapting the Python 2 examples in the API Playground and this library.

It was originally tested with Redcap version 7.4.7 and Python 3.5.  Select methods have been tested on Redcap 8.1.3.  This library will not work with Python 2 in all likelihood.

Only JSON output has been tested (not XML/CSV yet).

A notebook containing a template for unit tests has been provided, which itself has not been tested recently.

Currently, the following features are known to work in 8.1.3 and are being used in production code for a number of currently active NIH sponsored protocols:
- import records
- import file
- export records
- delete record

The following worked in 7.4.7 but have not been tested recently.  Similarly, the unit test notebook has not been recently updated.
- export data dictionary
- export events
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
```

#### Export Records from Redcap
```python
from pprint import print

# Export select fields from all events
data_export = rc.export_records(rawOrLabel='label', fields='consent_date, record_id')
pprint(data_export)  # If successful, data_export is a list of dicts
```
#### Import Records to Redcap
```python
import pandas as pd

# Import data, one record at a time from a pandas DataFrame
df_to_upload = pd.DataFrame('Your Data')
    for i in range(len(df_to_upload)):
        record_to_upload = df_to_upload.iloc[i].to_json(orient='columns')
        import_return = rc.import_records(data_to_upload=record_to_upload)
```
#### Import File to Redcap
```python
# Import a file into a repeating instrument, an apparently undocumented feature
import_response = rc.import_file(event='data_import_arm_1',
                                 field='redcap_field_name',
                                 filename='full_path_filename',
                                 record_id='1',
                                 repeat_instance='2',
                                )
```
#### Delete Entire Record from Redcap
```python
# This method is very convenient for development/testing, but use very carefully for production.
# Delete all data for Record ID 30
rc.delete_record(30)

# Bulk delete: delete Record IDs 1-14.
[rc.delete_record(id) for id in range(1, 15)]
```





