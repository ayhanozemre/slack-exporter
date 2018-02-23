import os
import json
from html_generator import make_single_content, make_multiple_content


DATA_FILE_NAME = 'slack-export-data'


def save(file_path, item):
    with open(file_path, "w") as f:
        f.write(item)
    return file_path


def get_or_create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def json_content_save(directory, export_type, content_payload):
    new_directory = os.path.join(directory, DATA_FILE_NAME)
    get_or_create_directory(new_directory)
    for chat_type, content in content_payload.items():
        file_path = os.path.join(new_directory, chat_type) + '.json'
        if isinstance(content, (dict, list)):
            save(file_path, json.dumps(content))


def single_html_content_save(directory, export_type, content_items):
    file_path = os.path.join(directory, DATA_FILE_NAME) + '.html'
    content = make_single_content(content_items)
    return save(file_path, content)


def multiple_html_content_save(directory, export_type, content_items):
    content_items = make_multiple_content(content_items)
    new_directory = os.path.join(directory, DATA_FILE_NAME)
    get_or_create_directory(new_directory)
    for file_name, content in content_items.items():
        file_path = os.path.join(new_directory, file_name) + '.html'
        save(file_path, content)


def save_items(directory, export_type, items):
    _map = {
        'multiple_html': multiple_html_content_save,
        'single_html': single_html_content_save,
        'json': json_content_save}
    func = _map[export_type]
    return func(directory, export_type, items)
