# Redcapy

----
### Overview

This code contains a subset of the available methods to access a Redcap 7 server instance using Python.  The Redcap API offers a number of additional features via their API.  To date, however, this focuses on the more commonly used methods pertaining to needs with our own active projects.

This code was tested with Redcap version 7.4.7 and Python 3.5.  Only JSON output has been tested.

A notebook containing a template for unit tests has been provided.

Currently, the following features are available:
- import records
- export records
- export data dictionary
- export events
- delete single record
- delete form


----
### Usage
```python
from redcap.redcapy import Redcapy
import os

# Using environment variables
redcap_token = os.environ['your project token string']
redcap_url = os.environ['redcap server url']

rc = Redcapy(api_token=redcap_token, redcap_url=redcap_url)
data_export = rc.export_records(rawOrLabel='label',
                    fields='consent_date, randomization_id, record_id')```
```



