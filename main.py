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
