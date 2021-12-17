import typing

from bs4 import BeautifulSoup
import requests
import json


def fetch_get(url: str) -> typing.Optional[BeautifulSoup]:
    print('Requesting ' + url)
    try:
        response = requests.get(
            url,
            timeout=10,
            cookies={
                'LanguageFilter': '13',
                'HearingImpaired': '0',
                'ForeignOnly': 'False',
                '__cfduid': "d1e731e5b7a9935b44ccb5831628069ed1543570650",
                '_ga': "GA1.2.1215724997.1513623994",
                'cf_clearance': "102f048a1c6d535a8f76e44907d5b8d0fa10f27d-1553880580-31536000-150",
                'cookieconsent_dismissed': "yes"
            },
            headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
        )
        print(response.status_code)
    except requests.exceptions.ReadTimeout:
        print('Timeout')
        return None

    return BeautifulSoup(response.text, features="html.parser")


def fetch_post(url: str, data: dict) -> typing.Optional[BeautifulSoup]:
    print('Requesting ' + url + ' with ' + json.dumps(data))
    try:
        response = requests.post(
            url,
            data,
            timeout=10,
            cookies={
                'LanguageFilter': '13',
                'HearingImpaired': '0',
                'ForeignOnly': 'False'
            },
            headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
        )
        print(response.status_code)
    except requests.exceptions.ReadTimeout:
        print('Timeout')
        return None

    return BeautifulSoup(response.text, features="html.parser")