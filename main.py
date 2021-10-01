import random
import re
import string
import argparse
import logging
import requests

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client
    
def load_usernames(usernames_file):
    '''
    Loads a list of usernames from `usernames_file`.

    Args:
        usernames_file(str): filename of file holding usernames

    Returns:
        usernames(list): a list of usernames
    '''
    with open(usernames_file) as file_handle:
        return [line.strip() for line in file_handle.readlines()]
    

def o365enum_activesync(usernames):
    '''
    Check if `usernames` exists using ActiveSync.

    Args:
        usernames(list): list of usernames to enumerate
    '''
    headers = {
        "MS-ASProtocolVersion": "14.0",
        "User-Agent": "Microsoft Office/16.0 (Windows NT 10.0; Microsoft Outlook 16.0.12026; Pro"
    }
    for username in usernames:
        state = 0
        for _ in range(0, args.num):
            response = requests.options(
                "https://outlook.office365.com/Microsoft-Server-ActiveSync",
                headers=headers,
                auth=(username, args.password)
            )

            if response.status_code == 200:
                state = 2
                break
            else:
                if 'X-MailboxGuid' in response.headers:
                    state = 1
                    break
        print("{},{}".format(username, state))

