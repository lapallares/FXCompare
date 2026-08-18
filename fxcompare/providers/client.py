"""
Shared HTTP client.
"""

from curl_cffi import requests


def session():
    return requests.Session(impersonate="chrome")
