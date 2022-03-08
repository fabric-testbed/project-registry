import os
import json


def load_choices(file_name: str = None) -> [str]:
    if file_name:
        file_path = os.path.join(os.path.dirname(__file__), 'data', file_name)
        with open(file_path) as file:
            file_dict = json.load(file)

        choices = list(file_dict['key_value_pairs'].keys())
        return choices

    return []
