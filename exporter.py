# -*- coding: utf-8 -*-
import os
import time
import logging
import argparse
from slackclient import SlackClient
from helpers import save_items

logging.basicConfig(format='[%(asctime)s] %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


class SlackExporter(object):
    RATE_LIMIT_WAITING_SECONDS = 60
    MESSAGE_FETCH_COUNT = 1000

    def __init__(self, *args, **kwargs):
        self.token = kwargs['token']
        self.slack_client = SlackClient(self.token)
        self.chat_types_map = {
            'channels': self.get_all_channel_messages,
            'groups': self.get_all_group_messages,
            'direct_messages': self.get_all_direct_messages
        }

    def check_me(self):
        rsp = self.slack_client.api_call('auth.test')
        assert rsp['ok'], rsp['error'].replace('_', ' ')
        return rsp

    def get_members(self):
        members = {}
        rsp = self.slack_client.api_call("users.list")
        for member in rsp['members']:
            profile = member['profile']
            profile['id'] = member['id']
            members[member['id']] = profile
        return members

    def get_channels(self):
        rsp = self.slack_client.api_call("channels.list")
        return rsp.get('channels', [])

    def get_groups(self):
        rsp = self.slack_client.api_call("groups.list")
        return rsp.get('groups', [])

    def direct_message_channels(self):
        rsp = self.slack_client.api_call('im.list')
        return rsp.get('ims', [])

    def get_messages(self, method, channel, latest=None):
        payload = {
            'channel': channel,
            'count': self.MESSAGE_FETCH_COUNT,
            'unreads': True,
            'inclusive': False
        }
        if latest:
            payload['latest'] = latest
        rsp = self.slack_client.api_call(method, **payload)
        messages = rsp.get('messages', [])
        if rsp.get('error') == 'ratelimited':
            time.sleep(self.RATE_LIMIT_WAITING_SECONDS)
            messages += self.get_messages(method, channel, latest=latest)
        if rsp.get('has_more'):
            messages += self.get_messages(
                method, channel, latest=messages[-1]['ts'])
        return messages

    def get_direct_messages(self, channel):
        return self.get_messages('im.history', channel)

    def get_channel_messages(self, channel):
        return self.get_messages('channels.history', channel)

    def get_group_messages(self, channel):
        return self.get_messages('groups.history', channel)

    def get_all_direct_messages(self):
        direct_channels = self.direct_message_channels()
        for channel in direct_channels:
            messages = self.get_direct_messages(channel['id'])
            messages.reverse()
            yield {'messages': messages,
                   'channel_info': channel}

    def get_all_group_messages(self):
        groups = self.get_groups()
        for group in groups:
            messages = self.get_group_messages(group['id'])
            messages.reverse()
            yield {'messages': messages,
                   'group_info': group}

    def get_all_channel_messages(self):
        channels = self.get_channels()
        for channel in channels:
            messages = self.get_channel_messages(channel['id'])
            messages.reverse()
            yield {'channel_info': channel,
                   'messages': messages}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Slack Exporter',
        usage='expoter.py --token <token> [options]',
        epilog='if you do not have archive access, use me'
    )
    parser.add_argument('--token', required=True,
                        help=('slack access token.'
                              'if you haven’t received tokens yet, follow me '
                              'https://api.slack.com/custom-integrations/'
                              'legacy-tokens'))
    parser.add_argument('--chat-type', help='select chat type',
                        choices=['channels', 'groups', 'direct_messages'])
    parser.add_argument('--directory', default='.', help='export directory')
    parser.add_argument('--log-level', default='INFO',
                        choices=['INFO', 'DEBUG', 'WARNING'], help='log level')
    parser.add_argument('--export-type', default='json',
                        choices=['json', 'single_html', 'multiple_html'],
                        help='export type')
    args = parser.parse_args()

    assert os.path.exists(args.directory), '%s does not exist' % args.directory
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    exporter = SlackExporter(token=args.token)
    exporter.check_me()
    logger.info('starting...')

    items = {'members': exporter.get_members()}
    for chat_type, func in exporter.chat_types_map.items():
        if args.chat_type and chat_type != args.chat_type:
            continue

        logger.info('%s start' % chat_type)
        data = [item for item in func()]
        items[chat_type] = data
        logger.info('%s done' % chat_type)
    save_items(args.directory, args.export_type, items)
