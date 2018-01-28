# smartAPI Profiler
Web application to automatically identify resources provided by a database
by "profiling" a web service response from the database. The application profiles
the web service response to create a keypath and value mapping where the keypath
contains one or more keys (strings) concatenated with a dot. The individual keys
are obtained by recursively traversing the web service response until the remaining
value is either a string or a list of strings.

To identify a resource provided by the database, the individual elements of
the keypath are then used to search Identifiers.org for a match to a resource name
or synonym. If a match is found, this is displayed as the value for the Mapped Resource.
If a match is not found, a sample value from the keypath-value mapping is used to find
resources whose values match the pattern of this keypath. Matching resources are
displayed as resources with a pattern match.

The application is used together with the [smartAPI Editor](http://smart-api.info/editor/)
and submits data to the `responseDataType` field of the Editor.


## Dependencies
* Python 2.7 and above or 3.x
* Tornado

## Running the App
To run the app: <br>
`python app.py`

To run in debug mode: <br>
`python app.py --debug=true`


