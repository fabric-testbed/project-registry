import json
import os
import re
from abc import ABC


class CoreApiOptions(ABC):
    """
    Core API Options object
    """
    api_endpoints: [str]
    description: str
    key_value_pairs: {}
    name: str
    options: [str]

    def __init__(self, file_name: str = None):
        if file_name:
            file_path = os.path.join(os.path.dirname(__file__), 'json_data', file_name)
            with open(file_path) as file:
                file_dict = json.load(file)
            self.name = file_dict['name']
            self.description = file_dict['description']
            self.api_endpoints = []
            for ep in file_dict['api_endpoints']:
                self.api_endpoints.append({"description": ep['description'], "endpoint": ep['endpoint']})
            self.key_value_pairs = []
            for key in file_dict['key_value_pairs'].keys():
                self.key_value_pairs.append({key: file_dict['key_value_pairs'][key]})
            self.options = sorted(list(file_dict['key_value_pairs'].keys()), key=lambda s: s.casefold())

    def __add__(self, other):
        combined = CoreApiOptions()
        # use name, description and endpoints of self object
        combined.name = self.name
        combined.description = self.description
        combined.api_endpoints = self.api_endpoints
        # combine distinct elements of key_value_pairs for self and other
        combined.key_value_pairs = self.key_value_pairs
        combined.options = self.options
        for pair in other.key_value_pairs:
            kv = pair.popitem()
            kvpair = {str(kv[0]): str(kv[1])}
            if kvpair not in combined.key_value_pairs:
                combined.key_value_pairs.append(kvpair)
                combined.options.append(str(kv[0]))
        combined.options = sorted(combined.options, key=lambda s: s.casefold())
        return combined

    def search(self, pattern: str = None) -> [str]:
        if pattern:
            found = [item for item in self.options if pattern.casefold() in item.casefold()]
        else:
            found = self.options
        return sorted(found, key=lambda s: s.casefold())


def array_difference(a, b): return [x for x in a if x not in b]


def is_valid_url(url: str = None) -> bool:
    """
    Validate URL format
    """
    url_regex = ("((http|https)://)(www.)?" +
                 "[a-zA-Z0-9@:%._\\+~#?&//=]" +
                 "{2,256}\\.[a-z]" +
                 "{2,6}\\b([-a-zA-Z0-9@:%" +
                 "._\\+~#?&//=]*)")

    url_check = re.compile(url_regex)

    if url and re.search(url_check, url):
        return True
    else:
        return False
