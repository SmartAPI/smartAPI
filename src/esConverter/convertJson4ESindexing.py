import argparse
import requests
import os.path
import json
import time
from future.utils import iteritems
from collections import OrderedDict


# Confirm program arguments
def confirmArguments():
    parser = argparse.ArgumentParser(description='Program to convert \
        Json formatted file from Swagger editor for Elastic Search indexing.')
    parser.add_argument('filename', nargs='?')
    args = parser.parse_args()

    if args.filename is not None:
        input_file = args.filename
        return input_file
    else:
        print('Usage: python convertJson4ESindexing.py [filename or uri]')
        exit()


# Get file contents
def getFileContents(filename):
    # Check if URL provided
    if(filename.startswith("http")):
        print('DEBUG: Get file from URL')
        r = requests.get(filename)
        if r.status_code == 200:
            print('DEBUG: Got the file')
            # file_contents = r.text
            json_file_contents = r.json()
            return json_file_contents
        else:
            print('ERROR: Unable to access URL. Failed with status code ', r.status_code)
            exit()
    else:
        # Check if local file exists with file name provided
        if(os.path.isfile(filename)):
            print('DEBUG: Local file exists!')
            # Read in file contents
            f = open(filename, 'r')
            file_contents = f.read()
            if(file_contents == '' or os.stat(filename).st_size == 0):
                print('ERROR: No content in ', filename)
                exit()
            else:
                print('DEBUG: File contents exist')
                json_file_contents = json.loads(file_contents)
                return json_file_contents
        else:
            print('ERROR: No file found')
            exit()


# Convert Swagger JSON file
def convert_file(the_file_contents):
    es_formatted_data = {}
    operations_list = []

    # Get each first level path key
    for key in the_file_contents.keys():
        # Modify object in paths
        if(key == "paths"):
            for pathname_key in the_file_contents[key]:
                # print("\n")
                # print("** Pathname: ", pathname_key)
                path_obj = {}
                for method_key in the_file_contents[key][pathname_key]:
                    # print("\n")
                    # print("** Method name: ", method_key)

                    # Convert path object
                    path_obj["httpOperation"] = method_key
                    path_obj["path"] = pathname_key

                    # Convert response object
                    for stuff in the_file_contents[key][pathname_key][method_key]:
                        response_list = []
                        if(stuff == "responses"):
                            response_obj = {}
                            for response in the_file_contents[key][pathname_key][method_key][stuff]:
                                response_obj["httpCode"] = response
                                for response_item in the_file_contents[key][pathname_key][method_key][stuff][response]:
                                    response_obj[response_item] = the_file_contents[key][pathname_key][method_key][stuff][response].get(response_item)
                            response_list.append(response_obj)
                            path_obj["responses"] = response_list
                        else:
                            path_obj[stuff] = the_file_contents[key][pathname_key][method_key].get(stuff)

                operations_list.append(path_obj)
            es_formatted_data["operations"] = operations_list
        else:
            es_formatted_data[key] = the_file_contents.get(key)

    # adding a meta field
    meta = {'timestamp': time.ctime()}
    es_formatted_data['meta'] = meta

    # return es_formatted_data
    key_ordered_data = order_data(es_formatted_data)
    return key_ordered_data

# Convert ES indexed file format to Swagger format
def convert_to_swagger(the_file_contents):
    swagger_formatted_data = {}

    # Get each first level path key
    for key in the_file_contents.keys():
        # Modify object in operations
        if(key == "operations"):
            # Iterate through objects and re-format
            path_obj = {}
            for operations_dict in the_file_contents[key]:
                http_obj = {}
                operations_obj = {}
                # print("\n** New operations object **")
                path_key = operations_dict['path']  # E.g. /gene
                http_operation_key = operations_dict['httpOperation']  # E.g. post or get

                for key, value in iteritems(operations_dict):
                    if(key == "path" or key == "httpOperation"):
                        continue
                    elif(key == "responses"):
                        # Process responses
                        http_response_obj = {}
                        for response in value:
                            http_code = response['httpCode']
                            response_obj = {}
                            for k, v in iteritems(response):
                                if(k != 'httpCode'):
                                    response_obj[k] = v

                        http_response_obj[http_code] = response_obj
                        operations_obj[key] = http_response_obj
                    else:
                        operations_obj[key] = value

                # Add to object
                http_obj[http_operation_key] = operations_obj

                # Check if path_key in path_obj
                if(path_key) in path_obj:
                    path_obj[path_key].update(http_obj)
                else:
                    path_obj[path_key] = http_obj

            # Add path object to data file
            swagger_formatted_data["paths"] = path_obj
        # Do not add _id and meta fields into converted file
        elif (key in ["_id", "meta"]):
            continue
        else:
            swagger_formatted_data[key] = the_file_contents.get(key)

    # return swagger_formatted_data
    key_ordered_data = order_data(swagger_formatted_data)
    return key_ordered_data


# Sort data to maintain key order
def order_data(data):
    key_sort_list = ['info', 'host', 'basePath', 'schemes', 'produces', 'consumes', 'tags', 'operations', 'paths']
    key_ordered_data = OrderedDict()

    for item in key_sort_list:
        if item in data:
            key_ordered_data[item] = data[item]
    return key_ordered_data


# Main Program #
if __name__ == '__main__':
    filename = confirmArguments()

    the_file_contents = getFileContents(filename)

    # es_formatted_data = convert_file(the_file_contents)

    swagger_formatted_data = convert_to_swagger(the_file_contents)
    print(swagger_formatted_data)