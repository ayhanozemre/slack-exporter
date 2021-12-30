import os
import json
from html_generator import make_single_content, make_multiple_content


DATA_FILE_NAME = 'slack-export'


def save(file_path, item):
    with open(file_path, "w") as f:
        f.write(item)
    return file_path


def get_or_create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def json_content_save(directory, export_type, conversations, members):
    new_directory = os.path.join(directory, DATA_FILE_NAME)
    get_or_create_directory(new_directory)

    members_file_path = os.path.join(new_directory, "members.json")
    if not os.path.exists(members_file_path):
        save(members_file_path, json.dumps(members))

    file_path = os.path.join(new_directory, "conversations.json")
    save(file_path, json.dumps(conversations))


def single_html_content_save(directory, export_type, conversations, members):
    file_path = os.path.join(directory, DATA_FILE_NAME) + '.html'
    content = make_single_content(conversations, members)
    return save(file_path, content)


def multiple_html_content_save(directory, export_type, conversations, members):
    content_items = make_multiple_content(conversations, members)
    new_directory = os.path.join(directory, DATA_FILE_NAME)
    get_or_create_directory(new_directory)
    for file_name, content in content_items.items():
        file_path = os.path.join(new_directory, file_name) + '.html'
        save(file_path, content)


def save_conversations(directory, export_type, conversations, members):
    _map = {
        'multiple_html': multiple_html_content_save,
        'single_html': single_html_content_save,
        'json': json_content_save}
    func = _map[export_type]
    return func(directory, export_type, conversations, members)
