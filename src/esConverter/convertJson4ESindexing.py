import argparse
import requests
import os.path
import json


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
	converted_data = {}
	operations_list = []
	
	# Get each first level path key 
	for key in the_file_contents.keys():

		# Modify value for schemes
		if(key == "schemes"):
			values = the_file_contents.get(key)
			values.append('https')
			converted_data[key] = values

		# Modify object in paths
		if(key == "paths"):
			for pathname_key in the_file_contents[key]:
				print("\n")
				print("** Pathname: ", pathname_key)
				path_obj = {}
				for method_key in the_file_contents[key][pathname_key]:
					print("\n")
					print("** Method name: ", method_key)

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
			converted_data["operations"] = operations_list
		else:
			cd = converted_data[key] = the_file_contents.get(key)

	# Print converted data		
	# print(json.dumps(converted_data, sort_keys=True, indent=4, separators=(',', ': ') ))
	return converted_data


## Main Program ##
if __name__ == '__main__':
	filename = confirmArguments()

	the_file_contents = getFileContents(filename)

	converted_data = convert_file(the_file_contents)


	
