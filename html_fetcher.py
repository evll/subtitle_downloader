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
                'ForeignOnly': 'False',
                '__cfduid': "dd86eacb41635e640a8a8c548aa74b4351565718962",
                '_ga': "GA1.2.1215724997.1513623994",
                'cf_clearance': "102f048a1c6d535a8f76e44907d5b8d0fa10f27d-1553880580-31536000-150",
                'cookieconsent_dismissed': "yes",
                'trc_cookie_storage': 'taboola%2520global%253Auser-id%3D4fb6e333-3c4c-44b0-85e8-3cf34d71d7d2',
                'nexagesuid': '1bd7a84756b94afa93888cfee43a3f8b',
                'scene': 'Vd_YtoUhvIuLvT2t-LFed8Pyi511224kH8XyYZNHG52pyhk6HYOa_7d8JBmHkaMx65sVUljAfSrUUVl3fuZDkfyA8SJAZ9ZDwJmTpcdcOWkj_sa7iMUljaX5CISSWi7N57A_0hBQvDrXM8RaTzlULPnoz7n2itIhV7yrQKzxDu_-RvS6_Z87r9GY-Cs0UsKkgbKwqvoyI1kkBpsDvac-E6UQ03leTb8CLHmpDRaXkB1SCBRhXJhgpjUZCUqEGHRDTW1PC_QZJtkU-fxOLs9Z7zWsz7JyYofonHQYl5XTKjUi9_kM_TlDHoNRnXaS65ePC99BAb3u9aaXNE3p7RoJ6TxDaj1X_kwiugPyxL958wxBtW-cSN9fcLWB79tyblhkU1KxtEXcuRDDkGuOJkIGtbvUY7WMOP3hE70vAnOOgV1cXV8yTgalT_OzPXj1Ur3q5_K2yCCPCrDORJl04djMOR4ODGQBe-K4FNRRZXvfRfZ9yZfmdgrVYuKbWC6_6_844Fm3PaiBfXMUMZestjv7yrSUFl7Oung59FLkHSQONU4HmoZl980oZDTA3CCNg_w7HxjBqbHxqyjf3KMAy_L3P8tNJD-YUPRKXmfjKU8gXfgx_oZIq51eIonkpNPgXmJxIxsq15Pp4k3aRmHl_7U6nxxA7Uz6PLRAEwD9qH3mhyBc8hePDOnNVB8_RcBhytSgB_10JWUXbfNOC4GXXDuMXEaFLtzTFjn1eQZS7bQ8VJFwF-ISDhrj60Awugp_v02q1OxBDWacWZ4qBpseIGWorx7gpZ8UqN2Z9hBHRjg7Nl3nrogYGOBp1Twe62IXhWTObbUI-UtMyKc23-2JhunCmeoWeGfv3vn8GlqaBqvlesgA4u29TZQQS-_fOBjNPXGdtBWGs9ahXwvMqt41agt_O7mjkibiNc9CG6dHP1BvEjeZNT66YrwVP6kwXxtRu5oQqy5L9wMbKMyu775B1oHvofH8K_bzlZCm4N5eOj0fauiQN-neC-Cn8aMBtrNzMYszyGSZlmmLN89mEpQnT-LQIhV6tgHOol1rWr_PC7YyJefVQ3Px5TgfvtQheXCTGwpCS9K06uG817fwXP30_avkdFsdge6ywUU9hzi_dFx3a2CuusCOA-OCaaw0IeupgJhEThKbk-NzV0bfOtDCzD7rzEmZRbsXJoV9qQxAeYqPSzZICMSGo0GJvor6yqPKXn87oTXrIfSl8PDnGlsTEGOtx7Qkfh5yxOu2AJd74mkY7RXsB6ynzO1WjwKvIDo1pCcZmtqCRIqYr3xGMe2ccjKEWg4mH08dCqacsOTbCcldGWg2cQ03YBpmQVIMmNp-gJ1OkX-10ydcAT6LMIOGJPoU_atBbGnfzLwtTk1Gc8sULf44AhFyVxwQEYN4wwxVt1dDa-F0KWgy0wQe_H2BeHQhE4kLP2XLZGJM7jmRPrQp-91oEGfOAKpIbXIW7Rkzwq0jwJoRDndfgAVmjZU1GvLhOxXqq8zu-MzowBC_eWwBtBnx09oOYrOyeBC8eSiXnHybQ9JSEA3E0nT-LwXtZak9K_mWatVw-6s9eBZLXF2VfZZP0hTPKxZBI9-FwqPi-hdwym5itc3F8Vnou4ytvYRiYy6fWN2Pez4gFE2xlFEjrp2KreA-GbKns0orFgKUlaLLXje-WboygOI4O9eCLZnfbJgIFEe35p51oM5jyZnbcJdB1k-Ia3hvvmKPzfR9OL5dj0d44vOJN2s79pKLRDSjzlCvL49XD3YAiffS_ivcJUoYMwH0_9Dbn9QEX0EhU0ptKqfn_nIHNizrcLYXet87Hr_wygHFCwLKjkTkhurnj76wwSkYC5l9V1cKieTfBZhdbDLU89f1BHY2Prp74Uin2sXH1h3yg-FlbsoZeFYVTrCfULDDqSEIaQKyohecJSCJjBXq4_0yB3AcWzHQ6WFWwxCZYuNJsKKr0yYoC8Kjefid0lPULoXDDBQIlXzCGEehVJswzuvLwdygvmTCfT0cBkqLIAYmjS8k484aUZCoTrev__9NpN1mgNZXgKdJwM6QO7lXIoMAl7P7ptK4jfgI6bo-xtJivxgeoxBdHxj8qRtQWneTMW8CjsvbZjnTwadNuloREp9Jupi16R_vrapOt41vC4sZiIZaC9eFQnnyOZQOUhmcreHH9n1w4Hzis4fT4zqfTRpY_tIc_50Govb7MoqIh00GfXOA3Ujq_8ClvRkVXWXOjQ4gB3jDhJEcoRH7HpJngGq0jMjKsdhXpj-G6gUmaDZEEQS4tC0yuBUP6tiSYrqlNFr46e4iE6q1PYagXMLR9kfmxgF2VpkQHQEh6ZcNgabi-EHlac4DEjarWM9RG1wG9wuodhB5fGybIzDJtdAcotjWM8cEMKhlW7Z5JNLnBatc2aO7diZIt0A93gN-Kq5pKALpgJebCe-xPZv-S7bDb7euZKVWVJMq9IUu9XXxdEBDBHYj6ePXPhWAtGsXnjykokSVo85UiK1Tu-ea-VTSgyhFgeRFW5Q1rpIukzCUcG0ihdROCbCsBY6174gQSjz49Vk1zFA1g6wIQBvImtjNgDNNkCpwvT5pOwqIjsHF1B38vRgCkJKh3Gsbhfq8TbLnwaF7N2F9Mk6PWD_8gO5qBdZpfr2rVU0MMnWXqcITScwo8pEQ8cqIAsawuBE-u2eTaVle_H3jUbX4sMR23PJm7rIFUYP-3Z_QzroZFcLgi9aSOeFaVzVcA_shWudiwwdSCFj9ok5VThZZqd43Go9YJZ8-PIGN9vlD214rul0uP8wDpzsJVNLkSikTnyCea5EYKGcLQAMkGpPDjrg2Jq6WU1GsREBaE4dPeE3n5ZUA08tLRTjtzX7re8PqaCPQLGXu5UoUPD5-lJtUA0yVgaGwuOEusiKBE1vh-RBAKH07SBwzeA4XL7Vz4whyfvimf1c3DFWxgAgBe2Y-1lCSk5bVtuu9Con9wEPuR18nAiG42KCdVVBEd4FGaX6kEiC0yLxQJtpWdbYZBckVc94hb3uQ6pdy8hnu1osy3fDalvZLjo9b0uqRxas61RFh47dFcTbUK3fa2x481s71pOvQmxtMPjpmkc_ebJwX7dXEVjy28UWyDarf-v3MQuk57cMMuT_ZKf8_heLKF5NFOEuilF7WLsUM_vtPsi82X-U8RNXqG3GhPG8In2HGDaaPcNWhgUVXSVe2a31JqNluOwmObJFcdacnR5vVOT8hSO1mOXoTuL0wijrKDaMjHg3KcfDUwWnZVCPk6I8suha71E7r'
            },
            headers={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
        )
        print(response.status_code)
    except requests.exceptions.ReadTimeout:
        print('Timeout')
        return None

    return BeautifulSoup(response.text, features="html.parser")