from datetime import datetime
from jinja2 import Environment, FileSystemLoader


TEMPLATE_ENV = Environment(loader=FileSystemLoader('templates'))


def render_to_template(template_name, context):
    template = TEMPLATE_ENV.get_template(template_name)
    return template.render(context)


def content_replacement(content, members):
    for member_id, member_info in members.items():
        mention_tag = '<@%s>' % member_id
        name = get_member_name(member_info)
        name_html = '<span style="color:red">' + name + '</span>'
        content = content.replace(mention_tag, name_html)
    # html blocker tags
    content = content.replace('<https', 'https')
    content = content.replace('png>', 'png ')
    return content


def timestamp_to_strftime(ts):
    return datetime.fromtimestamp(
        float(ts)).strftime('%Y-%m-%d %H:%M:%S')


def get_attachments_message(message):
    message_text = ''
    for item in message.get('attachments', []):
        message_text += item.get('text', '')
        message_text += item.get('fallback', '')
        message_text += item.get('title', '')
        actions = item.get('actions') or []
        action_text = [action.get('text', '')
                       for action in actions]
        message_text += ' '.join(action_text)
    return message_text


def get_file_message(message):
    message_text = ''
    for item in message.get('files', []):
        message_text += item.get('permalink_public', '')
    return message_text


def get_message(message):
    message_text = message.get('text', '')
    message_text += get_attachments_message(message)
    message_text += get_file_message(message)
    return message_text


def get_member_name(member_info, default_member_name='unknown-name'):
    if member_info is None:
        return default_member_name
    return member_info.get('display_name') or \
        member_info.get('email') or \
        member_info.get('real_name') or default_member_name


def get_message_member_id(message):
    if message.get('comment'):
        member_id = message['comment']['user']
    else:
        member_id = message.get('user')
    return member_id


def make_message_payload(member_display_name, message):
    message_text = get_message(message)
    message_date = timestamp_to_strftime(message['ts'])
    return {'date': message_date,
            'message': message_text,
            'member': member_display_name}


def message_content_handler(channel_id, display_name, messages, members):
    message_list = []
    for message in messages:
        member_id = get_message_member_id(message)
        member_display_name = get_member_name(members.get(member_id))
        message_payload = make_message_payload(member_display_name, message)
        message_list.append(message_payload)
    return {'channel_id': channel_id,
            'label': display_name,
            'messages': message_list}


def prepare_content_items(conversations, members):
    item_list = []
    for conversation in conversations:
        channel = conversation["channel_payload"]
        channel_id = channel["channel_info"]["id"]
        display_name = channel["channel_info"]["name"]
        processed_conversation = message_content_handler(
            channel_id, display_name, channel['messages'], members)
        item_list.append(processed_conversation)
    return item_list


def make_menu_html(items, hash_fragment=True):
    menu_items = {item['channel_id']: item['label'] for item in items}
    context = {'menu_items': menu_items, 'hash_fragment': hash_fragment}
    return render_to_template('menu.html', context)


def make_content_template(item):
    return render_to_template('content.html', {'item': item})


def make_content_html(menu, content):
    context = {'menu': menu, 'content': content}
    return render_to_template('main.html', context)


def make_multiple_content(conversations, members):
    contents = prepare_content_items(conversations, members)
    menu_html = make_menu_html(contents, hash_fragment=False)
    items = {'index': menu_html}
    for item in contents:
        html = make_content_template(item)
        clean_html = content_replacement(html, members)
        items[item['channel_id']] = clean_html
    return items


def make_single_content(conversations, members):
    contents = prepare_content_items(conversations, members)
    menu_html = make_menu_html(contents)
    content_html = ''
    for item in contents:
        html = make_content_template(item)
        content_html += html
    html = make_content_html(menu_html, content_html)
    result = content_replacement(html, members)
    return result
