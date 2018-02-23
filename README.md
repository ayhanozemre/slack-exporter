## Slack Exporter
Slack conversation exporter html/json

## Requirements

* Python 3.x

## Installation
        pip install -r requirements.txt

## Running

        # ps :  If you have a large conversations, use "--export-type=multiple_html"
        # single html all conversations
        python exporter.py --token <slack-token> --export-type=single_html --directory=/tmp/
        # json export all conversations
        python exporter.py --token <slack-token> --export-type=json --directory=/tmp/
        # json export only channels
        python exporter.py --token <slack-token> --export-type=json --chat-type=channels --directory=/tmp/
        # multiple html export only channels
        python exporter.py --token <slack-token> --export-type=multiple_html --chat-type=channels --directory=/tmp/

## Arguments
          Arguman    required/optinal   description
        --token TOKEN     required        slack token
        --chat-type       optional        channels|groups|direct_messages, default "all"
        --directory       optional        default "current" directory
        --log-level       optional        INFO|DEBUG|WARNING, default "INFO"
        --export-type     optional        json|single_html|multiple_html, default "json"