import os
import time
import logging
import argparse
import client
from helpers import save, save_conversations

logging.basicConfig(format='[%(asctime)s] %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

RATE_LIMIT_WAITING_SECONDS = 60
MESSAGE_FETCH_COUNT = 1000
DOWNLOAD_FILES = True #TODO: turn this into a CLI argument

file_index = 0 #avoiding duplicates in file names

def check_me():
    _, result = client.check_me()
    assert result["ok"], result["error"].replace("_", " ")
    return result


def get_channels(_type, cursor=None):
    channels = []
    _, result = client.get_conversations(
        conversation_type=_type, cursor=cursor)
    channels.extend(result["channels"])
    meta = result["response_metadata"]
    if meta["next_cursor"]:
        channels.extend(get_channels(_type, meta["next_cursor"]))
    return channels


def get_members(cursor=None):
    members = {}
    _, result = client.get_users(limit=10, cursor=cursor)
    meta = result["response_metadata"]
    for member in result["members"]:
        member_id = member["id"]
        members[member_id] = member
    if meta["next_cursor"]:
        members.update(get_members(meta["next_cursor"]))
    return members


def get_messages(channel, latest=None):
    messages = []
    _, result = client.get_messages(
        channel,
        latest=latest,
        inclusive=True,
        limit=MESSAGE_FETCH_COUNT)

    if result.get("error") == "ratelimited":
        time.sleep(RATE_LIMIT_WAITING_SECONDS)
        messages.extend(get_messages(channel, latest))
    else:
        result_messages = result["messages"]
        if latest is not None:
            result_messages.pop(0)
        messages.extend(result_messages)

    if messages:
        has_more = result.get("has_more")
        last_latest = messages[-1]["ts"]
        if latest != last_latest and has_more:
            messages.extend(get_messages(channel, last_latest))
    return messages

def get_file_links(messages):
    has_files_list = [msg["files"] for msg in messages if "files" in msg]
    files = [file for file_list in has_files_list for file in file_list] #flatten the file_list arrays
    downloadable = [file['url_private_download'] for file in files if "url_private_download" in file ]
    return downloadable

def get_files(messages):
    global file_index
    links = get_file_links(messages)
    if len(links) == 0:
        return
    for link in links:
        response = client.download_file(link)
        file_index += 1
        file_name = str(file_index) + '--' + link.split('/')[-1]
        path = os.path.join(args.directory, 'downloaded', file_name) #TODO this means the `downloaded` folder must be in the destination.
        save(path, response.content, mode='wb+')
    return links

def channel_handler(channel_type):
    for c_type in client.CONVERSATION_TYPES:
        if channel_type and channel_type != c_type:
            continue
        for channel in get_channels(c_type):
            messages = get_messages(channel['id'])
            messages.reverse()
            if DOWNLOAD_FILES: 
                files = get_files(messages)
            result = {
                "channel_info": channel,
                "messages": messages
                # can add files here later too
            }
            yield result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Slack Exporter",
        usage="expoter.py [options]",
        epilog="if you do not have archive access, use me"
    )
    parser.add_argument("--channel-type", help="select channel type",
                        choices=list(client.CONVERSATION_TYPES))
    parser.add_argument("--directory", default=".", help="export directory")
    parser.add_argument("--log-level", default="INFO",
                        choices=["INFO", "DEBUG", "WARNING"], help="log level")
    parser.add_argument("--export-type", default="json",
                        choices=["json", "single_html", "multiple_html"],
                        help="export type")
    args = parser.parse_args()

    assert os.path.exists(args.directory), "%s does not exist" % args.directory
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    logger.info("starting...")
    check_me()

    members = get_members()
    channels_payload = {"members": members, "channels": []}

    conversations = []
    for channel_payload in channel_handler(args.channel_type):
        conversation_payload = {
            "channel_type": args.channel_type,
            "channel_payload": channel_payload
        }
        conversations.append(conversation_payload)
    save_conversations(args.directory, args.export_type,
                       conversations, members)
