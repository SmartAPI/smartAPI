# Import to enable Python2/3 compatible code
from __future__ import print_function
from __future__ import unicode_literals
from future.utils import iteritems

import json
import re
import csv

from collections import OrderedDict
from operator import itemgetter


def get_input_data():
    """ Open file that contains keypath and values. """
    input_data_dict = {}
    with open('test-master_identifier_dictionary.txt') as input_file:
        reader = csv.reader(input_file, delimiter='\t')
        for line in reader:
            key = line[0]
            value = str(line[1])[1:-1]
            value = value.split(',').pop(0).strip('\'')
            input_data_dict[key] = value
    return input_data_dict


# Build dictionary of MIRIAM Registry entries
# Each datatype is an object in the dict incl. name, miriam_id,
# synonyms and pattern for value

# Use manually curated file of Identifiers.org resources
# to reduce pattern matches to very general patterns
def get_pattern_data():
    with open('./data/data_registry_MODIFIED2.json') as data_file:
        data = json.load(data_file)
    return data


# Find entries that match patterns for values in MIRIAM Registry
def find_pattern_matches(pattern_data, input_data_dict):
    """ Find IDs/Resource names from MIRAIM Registry
    where the value from the API response matches. """
    all_pattern_matches_id_name = {}

    # Loop through all dictionary entries
    for (k, v) in iteritems(input_data_dict):
        all_pattern_matches_dict = {}
        has_pattern_matches = True
        for item in pattern_data:
            p = re.compile(item["pattern"])
            # Test if pattern in json matches test pattern
            if p.match(v):
                has_pattern_matches = False
                miriam_id = str(item["id"])
                name = str(item["name"])
                all_pattern_matches_dict[miriam_id] = name

        # Add placeholder if no pattern matches are found
        if (has_pattern_matches):
            miriam_id = '0'
            name = 'None'
            all_pattern_matches_dict[miriam_id] = name

        # Sort by resource name for display in autocomplete
        sorted_all_pattern_matches_dict = OrderedDict(sorted(all_pattern_matches_dict.items(), key=itemgetter(1)))
        all_pattern_matches_id_name[k] = sorted_all_pattern_matches_dict
    return all_pattern_matches_id_name


def get_all_pattern_data():
    """ Build dictionary of All MIRIAM Registry entries.
    Each datatype is an object in the dict incl. name, miriam_id,
    synonyms and pattern for value. """
    with open('./data/data_registry.json') as data_file:
        all_registry_data = json.load(data_file)
    return all_registry_data


def make_pattern_dictionary(all_pattern_data):
    """ Generate a pattern dictionary with the MIRIAM ID as the key
    and the patterns as the value. """
    all_pattern_dict = {}
    for item in all_pattern_data:
        miriam_id = str(item["id"])
        pattern = str(item["pattern"])
        all_pattern_dict[miriam_id] = pattern
    return all_pattern_dict


# Main Program
if __name__ == '__main__':
    input_data_dict = get_input_data()
    pattern_data = get_pattern_data()
