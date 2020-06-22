[![Build Status](https://travis-ci.org/NCATS-Tangerine/translator-api-registry.svg?branch=master)](https://travis-ci.org/NCATS-Tangerine/translator-api-registry)

# translator-api-registry
This repo hosts the API metadata for the Translator project

## How to add your API

1. First, each API should create a separate folder to host its metadata. The folder "_example_api" provides basic template for adding API metadata, so you can start with copying "_example_api" folder and renaming it to your API name.
2. Second, fill in the metadata about your API according to the instruction. Also please refer to the existing examples like "[mygene.info](mygene.info)" and "[myvariant.info](myvariant.info)" APIs. See more details in the next section.
3. Add an entry to [API_LIST.yml](API_LIST.yml) file following the existing example. This is the master list of the APIs available in this repo. Our SmartAPI application will import all the API metadata based on this file.

If you have the permission, commit your changes to this repo. Otherwise, feel free to submit a pull-request. Please check the "build status" badge above, and make sure it's green after your changes. We run some validation tests in this "[tests.py](tests.py)" for each commit. (Tip: you can run `python tests.py` locally from the root of this repo to make sure all tests pass before you commit your code.)

### Specific notes for adding a [Reasoner API](https://github.com/NCATS-Tangerine/NCATS-ReasonerStdAPI)
In addition to follow the above steps, we recommend to add these extra info into your Reasoner API metadata:

    info:
        x-reasoner_standard_version: 0.9

    tags:
        name: translator
        name: reasoner

## How to create your OpenAPI v3 metadata

### Starting from the scratch
You can use [this editor](http://smart-api.info/editor/) to write/edit your API metadata. You can start with an existing metadata example from "[mygene.info](mygene.info/openapi_minimum.yml)" or "[myvariant.info](myvariant.info/openapi_minimum.yml)" APIs. The editor automatically validates your API metadata and gives a live preview of auto-generated API documentation.

This [OpenAPI GUI](http://smart-api.info/openapi-gui/) interface can also be useful for creating your API metadata from the scratch. But be aware of that this interface does not support any [SmartAPI extensions](https://github.com/SmartAPI/smartAPI-Specification/blob/OpenAPI.next/versions/smartapi-list.md) (those fields with "x-" prefix) we added to the standard OpenAPI v3 specifications. You can of course add extra SmartAPI fields after you export your metadata from the GUI interface to the editor.

### Converting from a Swagger/OpenAPI v2 metadata
If you already have an API metadata document in older Swagger/OpenAPI v2 specification. You can try this conversion tool to convert it to the latest OpenAPI v3 format, and then edit it in the [editor](http://smart-api.info/editor/):

https://mermade.org.uk/openapi-converter

http://openapiconverter.azurewebsites.net/


This converter is not perfect, but still a good starting point.

Tip: Feel free to play with your API metadata file with the tools we mentioned above, and commit your changes even when they are not fully complete or valid. As along as the metadata entry has not been added to the API_LIST.yml file (see below), you will be fine :-). When you are happy with your metadata, you can now move to the next step to add it to the API_LIST.yml file.

A [code snippet](https://github.com/PriceLab/translator-bigquery-api/blob/6d652ec28d0ae7b893395b3e3c360c9d5b144fe3/app/api/bigquery/endpoints/metadata.py#L115) to convert [flask-restful](http://flask-restful.readthedocs.io) auto-generated swagger v2 specification to SmartAPI metedata, kindly provided by @JohnCEarls.


## API_LIST.yml file
This is a YAML file at the root of this repo to keep track of all APIs available in this repo. Our SmartAPI application will import all the API metadata based on this file and render an API registry web frontend.

For each API, you just need to add a text block like this:

    - metadata: mygene.info/openapi_minimum.yml
      translator:
          - returnjson: true
            notes: ""

* ***metadata*** field

  The value of this field should be either the URL or the relative path pointing to the API metadata. The API metadata should follow [OpenAPI specifications](https://www.openapis.org/), in either JSON or YAML format. Specifically, we support OpenAPI v3 specification documented [here](https://github.com/OAI/OpenAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md), plus the SmartAPI extensions documented [here](https://github.com/SmartAPI/OpenAPI-Specification/blob/OpenAPI.next/versions/3.0.0.md).

* ***translator*** field

  This serves as the placeholder for any translator project specific API properties, e.g. adding some API-specific notes.

  * How to propose a new translator.* field?

    As we expand our list of APIs, we will need to expand our metadata fields as we needed. To do so, you can:
      * discuss it with us at our slack channel (#arch-working-group)
      * open an issue in this repo
      * submit a pull-request for your modified [API_LIST.yml](API_LIST.yml) file

## CORS support
If you want users are able to request your API from the browser, e.g. in a web application, your API should support [CORS](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing). We recommend every translator API to support CORS. Depending on your web server (e.g. Apache or Nginx) and/or the web framework (e.g. Django, Flask, Tornado) you use, you can find the relevant instruction to enable CORS for your API [here](https://enable-cors.org/), or via Google.

## How to pick URIs for annotating input parameters or the response data object?
Typically for a JSON-based REST API, we use URIs to annotate both the acceptable parameter value types and the fields from the response data object, both in  [OpenAPI](https://www.openapis.org/) metdata files and JSON-LD context files. You can find some examples for "[mygene.info](mygene.info)" and "[myvariant.info](myvariant.info)" APIs.

To help you decide which URIs to use, we maintain a "[ID_MAPPING.csv](ID_MAPPING.csv)" file to keep records of all URIs we will use. Feel free to add URIs for additional field types. Please make sure not to break the csv format, as that will break github's nice csv rendering and search features.

In general, we like to use the URIs from these repositories (also in that priority order)：
  1. Identifiers.org
  2. purl.uniprot.org (?)
  3. [please add]


## Know a knowledge source useful for Translator, but no API available?
You can add a knowledge source (or datasets) to this [DATASET_LIST.yml](DATASET_LIST.yml) file. Follow the instruction and existing entries there.

Translator team members monitor this list and can potentially build an API to serve that particulara knowledge source, so that it can be better integrated in the rest of Translator API ecosystem.
