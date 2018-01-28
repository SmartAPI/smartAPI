# Imports to enable Python2/3 compatible code
from __future__ import print_function
from future.utils import iteritems

import json  # noqa
import requests  # noqa
from collections import OrderedDict
from operator import itemgetter


def get_miriam_datatypes():
    """ Get MIRIAM Identifiers for Resources. """
    miriamws = "http://www.ebi.ac.uk/miriamws/main/rest/datatypes/"
    r = requests.get(miriamws, headers={"Accept": "application/json"})

    if r.status_code == 200:
        response = r.text
        data = json.loads(response)
        return data
    else:
        # Get data from file and return to continue processing
        with open('./data/miriam_datatypes.json') as data_file:
            data = json.load(data_file)
        return data


def build_miriam_identifier_dictionary(miriam_datatype_obj):
    """ Build dictionary mapping Resource Name->Identifier
    using data returned from  get_miriam_datatypes(). """
    datatype_dict = {}

    for (root, value_obj) in iteritems(miriam_datatype_obj):
        for k_v_obj in value_obj:
            # Build-up dict with the name, e.g. pir, as Key and
            # Miriam ID as the Value to lookup by the name
            key = k_v_obj['name'].lower()
            value = k_v_obj['id']
            datatype_dict[key] = value
    return datatype_dict


def build_miriam_name_dictionary(miriam_datatype_obj):
    """ Build dictionary mapping MIRIAM ID->Resource Name
    to use for autocomplete in the form. """
    miriam_name_dict = {}

    for (root, value_obj) in iteritems(miriam_datatype_obj):
        for k_v_obj in value_obj:
            # Build-up dict with the ID as Key and
            # resource name as the Value
            key = k_v_obj['id']
            value = k_v_obj['name']
            miriam_name_dict[key] = value
    # Sort dict for display in autocomplete
    sorted_datatype_dict = OrderedDict(sorted(miriam_name_dict.items(), key=itemgetter(1)))
    return sorted_datatype_dict


def build_miriam_autocomplete_data(miriam_datatype_obj):
    """ Build MIRIAM ID / Name Autocomplete data structure
    From: [{'MIR:00000001': 'Wikipedia'}, {'MIR:0000007': 'Some Resource'}]
    To: [{value: 'MIR:00000001', label: 'Wikipedia'},
    {value: 'MIR:0000007', label: 'Some Resource'}]. """
    autocomplete_data = []
    # NOTE: Autocomplete data needs to be added into children section
    # [{'text': 'All Resources', 'children': [{}]}]
    # autocomplete_data_deque = deque()

    for (root, value_obj) in iteritems(miriam_datatype_obj):
        for k_v_obj in value_obj:
            autocomplete_obj = {}
            autocomplete_obj['id'] = str(k_v_obj['id'])
            autocomplete_obj['text'] = str(k_v_obj['name'])
            autocomplete_data.append(autocomplete_obj)
    return autocomplete_data


# Main Program
if __name__ == '__main__':
    miriam_datatype_obj = get_miriam_datatypes()
    miriam_datatype_dict = build_miriam_identifier_dictionary(miriam_datatype_obj)
    build_miriam_name_dictionary(miriam_datatype_obj)
    miriam_autocomplete_data = build_miriam_autocomplete_data(miriam_datatype_obj)
