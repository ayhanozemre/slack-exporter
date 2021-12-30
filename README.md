# Slack Exporter

Slack conversations exporter html/json

## Requirements
* `Python 3.x`
* requests
* jinja2
 

## Installation
- pip install -r requirements.txt
- Set your slack token to env `SLACK_USER_TOKEN`

## How To Make Slack App
 - To create a Slack application, open `https://api.slack.com/apps` in the browser.
 - If we are not logged in, press the `Create New App` button on the page that opens after logging in.
 - Select the `From scratch` option in the popup that appears.
 - Select the App Name and the slack workspace you want to backup and press the `Create App` button.
 - From the `Basic information` tab, click on the `Permissions` tab under `Add features and functionality`.
 - Download the page and come to the `Scopes` section.
 - Add the following permissions by clicking the 'Add an OAuth Scope' button under 'User Token Scopes'.
 8 - `channels:history,channels:read,groups:history,groups:read,identify`
     `im:history,im:read,mpim:history,mpim:read,usergroups:read,users.profile:read`
     `users:read,users:read.email`
 - After adding the necessary permissions, the `install to workspace` button under `OAuth Tokens for Your Workspace` becomes active.
 - Confirm the permissions you have given in the window that opens by clicking the button and the necessary user token is created.

## Running
ps :  If you have a large conversations, use `--export-type=multiple_html`

Single html expor

    python exporter.py --export-type=single_html --directory=/tmp/
Json export

    python exporter.py <slack-token> --export-type=json --directory=/tmp/
Json export with channel type
    
    python exporter.py --export-type=json --channel-type=public_channel --directory=/tmp/
Multiple html export with channel type

    python exporter.py --export-type=multiple_html --channel-type=public_channel --directory=/tmp/

## Parameters
        Parameter    required/optinal   description
        --channel-type    optional   im|mpim|public_channel|private_channel. default "all"
        --directory       optional        default "current" directory
        --log-level       optional        INFO|DEBUG|WARNING, default "INFO"
        --export-type     optional        json|single_html|multiple_html, default "json"