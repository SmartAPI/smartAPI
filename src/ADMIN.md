# Admin.py Usage Guide

The `admin.py` file is a data administration module. Here the indices are built, populated, restored and updated.

## Restore Smart API  

#### `restore_from_file(filename=file)`   
- **Description:** Used to restore Smart APIs from a JSON file. It reads the data from the specified JSON file and restores the Smart APIs accordingly.
- **Parameters:**  
  - `filename` (str): The path to the JSON file containing Smart API data.

```python
from admin import restore_from_file

file="/path/to/file.json"
restore_from_file(filename=file)
```  

#### `restore_from_s3(filename=None, bucket="smartapi")`

- **Description:** Used to restore Smart APIs from an AWS S3 bucket. It retrieves the latest backup file from the specified bucket and restores the Smart APIs.
- **Parameters:**  
  - `filename` (str, optional): The name of the backup file in the S3 bucket. If not provided, it retrieves the latest backup file.
  - `bucket` (str, optional): The name of the S3 bucket where backup files are stored. Default is "smartapi".


## Building the MetaKG Index

####  `refresh_metakg(reset=True, include_trapi=True)`

- **Description:** Refreshes the MetaKG index.
- **Parameters:**
  - `reset` (optional, default=True): If True, resets the MetaKG index.
  - `include_trapi` (optional, default=True): If True, includes TRAPI (Translator Reasoning API) data during the refresh.

```python
from admin import refresh_metakg
refresh_metakg()
```

## Building the ConsolidatedMetaKG Index

#### `consolidate_metakg(reset=True)`

- **Description:** Consolidates MetaKG edge data into documents based on a subject-predicate-object key. It creates an index with the groups, facilitating efficient access and management of MetaKG-related information.
- **Parameters:**
  - `reset` (optional, default=True): If True, resets the ConsolidatedMetaKG index.

Note: the index, `smartapi_docs_metakg`, **must be available** --build with `refresh_metakg()`.

```python
# if not run already - 
from admin import refresh_metakg
refresh_metakg()
# then run to build consolidated index
from admin import consolidate_metakg
consolidate_metakg()
```

#### `refresh_has_metakg()`

- **Description:** Updates the '`has_metakg`' attribute for SmartAPI objects. It iterates through all SmartAPI objects, verifying their existence in the Meta-Knowledge Graph and updating the '`has_metakg`' attribute accordingly.

```python
from admin import refresh_has_metakg
refresh_has_metakg
```