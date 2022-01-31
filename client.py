import os
import json
from urllib.parse import urlencode
from http import HTTPStatus
import requests

SLACK_USER_TOKEN = os.getenv('SLACK_USER_TOKEN')
assert SLACK_USER_TOKEN is not None, 'slack token not found!'

BASE_URL = "https://slack.com"

CONVERSATION_TYPE_DM = "im"
CONVERSATION_TYPE_GROUP = "mpim"
CONVERSATION_TYPE_PUBLIC = "public_channel"
CONVERSATION_TYPE_PRIVATE = "private_channel"

CONVERSATION_TYPES = (
    CONVERSATION_TYPE_PUBLIC,
    CONVERSATION_TYPE_PRIVATE,
    CONVERSATION_TYPE_DM,
    CONVERSATION_TYPE_GROUP
)


def request(method, uri, querystring=None, payload=None, headers=None):
    data = {"token": SLACK_USER_TOKEN}
    if payload is not None:
        data.update(payload)

    url = BASE_URL + '/' + uri
    if querystring is not None:
        qs = {k: v for k, v in querystring.items() if v is not None}
        url += "?{qs}".format(qs=urlencode(qs))

    rsp = requests.request(method, url, data=data, headers=headers)
    return rsp.status_code, rsp.content


def api_request(func):
    def wrapper(*args, **kwargs):
        status, result = func(*args, **kwargs)
        status_ok = status == HTTPStatus.OK
        result = json.loads(result)
        return status_ok, result
    return wrapper


@api_request
def check_me():
    return request("post", "api/auth.test")


@api_request
def get_conversations(conversation_type, cursor=None, limit=None):
    qs = {
        "types": conversation_type,
        "cursor": cursor,
        "limit": limit,
        "exclude_archived": False
    }
    return request("post", "api/conversations.list", querystring=qs)


@api_request
def get_messages(channel, inclusive=False, limit=100, latest=None):
    qs = {
        "channel": channel,
        "inclusive": inclusive,
        "limit": limit,
        "latest": latest
    }
    return request("post", "api/conversations.history", querystring=qs)


@api_request
def get_users(cursor=None, limit=None):
    qs = {"cursor": cursor, "limit": limit}
    return request("post", "api/users.list", querystring=qs)

def download_file(url):
    headers = {'Authorization': f'Bearer {SLACK_USER_TOKEN}'}
    return requests.get(url, stream = True, headers=headers)
