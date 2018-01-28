import json


def build_miriam_url_dictionary():
    """ Build dictionary mapping MIRIAM ID to URL
    from full Identifiers.org resource information. """
    with open('./data/data_registry.json') as data_file:
        data = json.load(data_file)

    url_dict = {}
    for key in data:
        url_key = key["id"]
        url_value = key["url"]
        url_dict[url_key] = url_value
    return url_dict


# Main Program
if __name__ == '__main__':
    data_registry_url_dict = build_miriam_url_dictionary()
