import json
import re
import time
import zipfile
import requests
import typing
from bs4 import BeautifulSoup
from pathlib import Path
import sys


def extract_release_info(filename: str, ignore_key_count: int = 0) -> dict:
    """Parse file name and return a dictionary with the following keys:
    episode, quality, resolution, group
    If some info is not detected or is not relevant, the key will not be included.

    If ignoreKeyCount is provided, that amount of keys will be excluded from the return.
    This is useful for less strict comparison of titles.
    """
    quality_patterns = {'bluray', 'bdrip', 'hdrip', 'web-dl', 'dvdscr', 'web[^\-]', 'webrip'}
    resolution_patterns = {'720p', '1080p'}

    episode_matches = re.search(r's\d\de\d\d', filename, flags=re.IGNORECASE)
    quality_matches = {}
    resolution_matches = {}
    group_matches = {}
    if ignore_key_count < 3:
        quality_matches = re.search(r'\b(' + '|'.join(quality_patterns) + r')\b', filename, flags=re.IGNORECASE)
    if ignore_key_count < 2:
        resolution_matches = re.search(r'\b(' + '|'.join(resolution_patterns) + r')\b', filename, flags=re.IGNORECASE)
    if ignore_key_count < 1:
        filtered_filename = re.sub(r'\[.+\]', '', filename)
        group_matches = re.search(r'-(\w+)$', filtered_filename)

    return dict((key, value) for key, value in {
        'episode': episode_matches[0] if episode_matches else None,
        'quality': quality_matches[1] if quality_matches else None,
        'resolution': resolution_matches[0] if resolution_matches else None,
        'group': group_matches[1] if group_matches else None
    }.items() if value)


def find_movie_title_in_dir(dir_path: str) -> tuple:
    def extract_movie_title_from_filename(filename: str) -> tuple:
        """Returns a tuple where the first element is movie title with spaces and the second one is year.
        The year is not available for series, in that case the second value is None.
        """
        matches = re.match(r'(.+)(2\d{3})', filename)
        if matches:
            return matches[1].replace('.', ' ').replace('nt ', "n't ").strip(), matches[2]

        series_matches = re.match(r'(.+)s\d\de\d\d', filename, flags=re.IGNORECASE)
        if series_matches:
            return series_matches[1].replace('.', ' ').replace('nt ', "n't ").strip(), None

        return filename.replace('.', ' ').replace('nt ', "n't ").strip(), None

    movie_extensions = {'avi', 'mkv', 'mp4'}
    current_dir = Path(dir_path)
    for entry in current_dir.iterdir():
        if entry.suffix[1:] in movie_extensions:
            return (
                *extract_movie_title_from_filename(' '.join(entry.name.split('.')[:-1])),
                '.'.join(entry.name.split('.')[:-1])
            )


def fetch_html(url: str) -> BeautifulSoup:
    print('Requesting ' + url)
    response = requests.get(
        url,
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

    return BeautifulSoup(response.text, features="html.parser")


def fetch_post_html(url: str, data: dict) -> BeautifulSoup:
    print('Requesting ' + url + ' with ' + json.dumps(data))
    response = requests.post(
        url,
        data,
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

    return BeautifulSoup(response.text, features="html.parser")


def check_release_info(release_info: dict, subtitle_spans: list, ignore_key_count: int):
    """Compare source release info with release info extracted from subscene result spans
    """
    for subtitle_span in subtitle_spans:
        entry_release_info = extract_release_info(subtitle_span.string.strip(), ignore_key_count)
        all_match = True
        for key, value in release_info.items():
            if not entry_release_info.get(key) or value.lower() != entry_release_info.get(key).lower():
                all_match = False
                break
        if all_match:
            return subtitle_span


def download_from_opensubtitles(
        movie_title: str,
        quality: typing.Optional[str],
        group: typing.Optional[str],
        year: typing.Optional[int]
) -> bool:
    """returns False if no subtitles were found or True if they were found and downloaded
    """
    searchable_title = movie_title.replace(' ', '+');
    if year:
        searchable_title += '+' + year;
    search_html = fetch_html(
        'https://www.opensubtitles.org/en/search2?MovieName=' + searchable_title +
        '&id=8&action=search&SubLanguageID=eng&Season=&Episode=&SubSumCD=&Genre=&MovieByteSize=&MovieLanguage=&' +
        'MovieImdbRatingSign=1&MovieImdbRating=&MovieCountry=&MovieYearSign=1&MovieYear=&MovieFPS=&SubFormat=&' +
        'SubAddDate=&Uploader=&IDUser=&Translator=&IMDBID=&MovieHash=&IDMovie='
    )

    download_rows = search_html.select('.change.expandable')

    if len(download_rows) == 0:
        return False

    download_links = []
    for download_row in download_rows:
        release_text = download_row.find_all(string=re.compile(quality + '.+' + group))
        if not release_text:
            release_text = download_row.find_all(string=re.compile(quality))
        if release_text:
            print(release_text[0])
            download_link = download_row.find('a', href=re.compile('/en/subtitleserve/sub/'))
            hearing_impaired = download_row.find_all('img', title='Subtitles for hearing impaired')
            if hearing_impaired:
                download_links.append(download_link['href'])
            else:
                download_links.insert(0, download_link['href'])

    if download_links:
        print('Download zip from ' + 'https://www.opensubtitles.org' + download_links[0])
        subtitle_response = requests.get(
            'https://www.opensubtitles.org' + download_links[0],
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0',
                'referer': 'https://www.opensubtitles.org/en/subtitleserve/sub/11111'
            }
        )

        zip_path = '/home/jevgenij/Downloads/subtitle.zip'
        with open(zip_path, 'wb') as output:
            output.write(subtitle_response.content)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('.')

        return True

    return False


def download_from_addic7ed(movie_title: str, episode: str, group: typing.Optional[str]) -> bool:
    """returns False if no subtitles were found or True if they were found and downloaded
    """
    search_html = fetch_html(
        'http://www.addic7ed.com/srch.php?search=' + movie_title.replace(' ', '+') + '+' + episode +
        '&Submit=Search'
    )
    # we might have multiple results, so if so, one more click is needed
    if search_html.find('title').text.strip().startswith('Search'):
        result_links = search_html.find_all('a', debug=True)
        if not result_links:
            return False

        # for now we simply take first link, but if needed, look for most suitable title like below
        # for result_link in result_links:
        #     comparable_title = re.sub(r'\s+\-\s.+$', '', result_link.text)

        search_html = fetch_html('http://www.addic7ed.com/' + result_links[0]['href'])

    download_links = search_html.select('.buttonDownload')
    matching_download_link = None
    english_download_link = None
    if len(download_links) > 0:
        for download_link in download_links:
            lang_container = download_link.parent.find_previous_sibling('td', 'language')
            group_container = download_link.find_parent('table').find('tr').find('td', 'NewsTitle')
            if lang_container.text.strip() == 'English' and \
                    group and group_container.text.lower().find(group.lower()) != -1:
                matching_download_link = download_link
                print('Found group match for ' + group)
                break
            elif lang_container.text.strip() == 'English':
                english_download_link = download_link

        if english_download_link and not matching_download_link:
            print(f'No group match for {group}, taking first English match')
            matching_download_link = english_download_link;

        if matching_download_link:
            print('Downloading ' + 'http://www.addic7ed.com' + matching_download_link['href'])

            subtitle_response = requests.get(
                'http://www.addic7ed.com' + matching_download_link['href'],
                headers={'referer': 'http://www.addic7ed.com'}
            )
            print(subtitle_response.status_code)
            subtitle_path = './' + movie_title.replace(' ', '_') + '.srt'  # XXX use a file name without extension
            with open(subtitle_path, 'wb') as output:
                output.write(subtitle_response.content)

            return True


directory = sys.argv[1] if len(sys.argv) == 2 else '.'

movie_dir_search_result = find_movie_title_in_dir(directory)
if movie_dir_search_result:
    movie_title, movie_year, movie_filename = movie_dir_search_result
else:
    print('No movie was found in this dir')
    raise SystemExit

# if it's series, give priority to addic7ed
release_info = extract_release_info(movie_filename)
# some series have year as a part of the title (e.g. Happy! (2017)), so concatenate them in such cases
if 'episode' in release_info.keys() and movie_year:
    movie_title = movie_title + ' ' + movie_year

downloaded_from_addic7ed = False;
if 'episode' in release_info:
    downloaded_from_addic7ed = download_from_addic7ed(movie_title, release_info['episode'], release_info['group'])

if downloaded_from_addic7ed:
    raise SystemExit

if 'episode' in release_info and ' and ' in movie_title:
    downloaded_from_addic7ed = download_from_addic7ed(
        movie_title.replace(' and ', ' %26 '),
        release_info['episode'],
        release_info['group']
    )

if downloaded_from_addic7ed:
    raise SystemExit

downloaded_from_opensubtitles = download_from_opensubtitles(
    movie_title,
    release_info['quality'] if 'quality' in release_info else '',
    release_info['group'],
    movie_year
)
if downloaded_from_opensubtitles:
    raise SystemExit

search_html = fetch_post_html(
    'https://subscene.com/subtitles/searchbytitle',
    {'query': movie_title, 'l': ''}
)
# this might be giving too many results, having the check below in mind
result_links = search_html.select('.exact + ul .title a')
# XXX for series add a map of season number to textual representation and use it to filter the correct title
if len(result_links) == 0:
    result_links = search_html.select('.search-result li:first-child .title a')

for result_link in result_links:
    if movie_year is None or movie_year in result_link.string or str(int(movie_year) - 1) in result_link.string:
        time.sleep(3)
        list_html = fetch_html('https://subscene.com' + result_link['href'])
        print('Looking for ' + movie_filename)
        subtitle_spans = list_html.select('.language-filter + table .a1 span:nth-child(2)')

        prev_release_info_details = 0
        for ignore_key_count in range(0, 3):
            release_info = extract_release_info(movie_filename, ignore_key_count)

            if len(release_info.keys()) == prev_release_info_details:
                break

            prev_release_info_details = len(release_info.keys())

            print('Matching with ' + json.dumps(release_info))
            subtitle_span_match = check_release_info(release_info, subtitle_spans, ignore_key_count)

            if subtitle_span_match:
                print('Downloading ' + subtitle_span_match.string.strip())
                subtitle_link = subtitle_span_match.find_parent('a')

                time.sleep(3)
                subtitle_html = fetch_html('https://subscene.com' + subtitle_link['href'])
                subtitle_link = subtitle_html.select_one('#downloadButton')
                print('Download zip from ' + 'https://subscene.com' + subtitle_link['href'])
                subtitle_response = requests.get(
                    'https://subscene.com' + subtitle_link['href'],
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
                zip_path = '/home/jevgenij/Downloads/subtitle.zip'
                with open(zip_path, 'wb') as output:
                    output.write(subtitle_response.content)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('.')

                raise SystemExit

