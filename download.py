import json
import re
import zipfile
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import sys


def extract_release_info(filename: str, ignore_key_count: int = 0) -> dict:
    """Parse file name and return a dictionary with the following keys:
    episode, quality, resolution, patterns
    If some info is not detected or is not relevant, the key will not be included.

    If ignoreKeyCount is provided, that amount of keys will be excluded from the return.
    This is useful for less strict comparison of titles.
    """
    quality_patterns = {'bluray', 'bdrip', 'hdrip', 'web-dl', 'dvdscr', 'web', 'webrip'}
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
        group_matches = re.search(r'-(\w+)$', filename)

    return dict((key, value) for key, value in {
        'episode': episode_matches[0] if episode_matches else None,
        'quality': quality_matches[1] if quality_matches else None,
        'resolution': resolution_matches[0] if resolution_matches else None,
        'group_matches': group_matches[1] if group_matches else None
    }.items() if value)


def find_movie_title_in_dir(dir_path: str) -> tuple:
    def extract_movie_title_from_filename(filename: str) -> tuple:
        """Returns a tuple where the first element is movie title with spaces and the second one is year.
        The year is not available for series, in that case the second value is None.
        """
        matches = re.match(r'(.+)(2\d{3})', filename)
        if matches:
            return matches[1].replace('.', ' ').strip(), matches[2]

        series_matches = re.match(r'(.+)s\d\de\d\d', filename, flags=re.IGNORECASE)
        if series_matches:
            return series_matches[1].replace('.', ' ').strip(), None

        return filename.replace('.', ' ').strip(), None

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
    response = requests.get(url, cookies={'LanguageFilter': '13', 'HearingImpaired': '0', 'ForeignOnly': 'False'})
    print(response.status_code)

    return BeautifulSoup(response.text, features="html.parser")


def check_release_info(release_info: dict, subtitle_spans: list, ignore_key_count: int):
    """Compare source release info with release info extracted from subscene result spans
    """
    for subtitle_span in subtitle_spans:
        entry_release_info = extract_release_info(subtitle_span.string.strip(), ignore_key_count)
        all_match = True
        for key, value in release_info.items():
            if value != entry_release_info.get(key):
                all_match = False
                break
        if all_match:
            return subtitle_span


directory = sys.argv[1] if len(sys.argv) == 2 else '.'

movie_dir_search_result = find_movie_title_in_dir(directory)
if movie_dir_search_result:
    movie_title, movie_year, movie_filename = movie_dir_search_result
else:
    print('No movie was found in this dir')
    raise SystemExit

# if it's series, give priority to addic7ed
release_info = extract_release_info(movie_filename)
if 'episode' in release_info:
    search_html = fetch_html(
        'http://www.addic7ed.com/srch.php?search=' + movie_title.replace(' ', '+') + '+' + release_info['episode'] +
        '&Submit=Search'
    )
    # XXX if multiple results are present, try the first one or check names
    # e.g. http://www.addic7ed.com/srch.php?search=fam+s01e05&Submit=Search
    download_links = search_html.select('.buttonDownload')
    english_download_link = None
    if len(download_links) > 0:
        for download_link in download_links:
            lang_container = download_link.parent.find_previous_sibling('td', 'language')
            if lang_container.text.strip() == 'English':
                english_download_link = download_link
                break

        if english_download_link:
            print('Downloading ' + 'http://www.addic7ed.com' + english_download_link['href'])

            subtitle_response = requests.get(
                'http://www.addic7ed.com' + english_download_link['href'],
                headers={'referer': 'http://www.addic7ed.com'}
            )
            print(subtitle_response.status_code)
            subtitle_path = './subs.srt'
            with open(subtitle_path, 'wb') as output:
                output.write(subtitle_response.content)

            raise SystemExit


search_html = fetch_html('https://subscene.com/subtitles/title?q=' + movie_title.replace(' ', '+') + '&l=')
result_links = search_html.select('.exact + ul .title a')  # this might be giving too many results, having the check below in mind
# XXX for series add a map of season number to textual representation and use it to filter the correct title
if len(result_links) == 0:
    result_links = search_html.select('.search-result li:first-child .title a')
for result_link in result_links:
    if movie_year is None or movie_year in result_link.string:
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

                subtitle_html = fetch_html('https://subscene.com' + subtitle_link['href'])
                subtitle_link = subtitle_html.select_one('#downloadButton')
                print('Download zip from ' + 'https://subscene.com' + subtitle_link['href'])
                subtitle_response = requests.get('https://subscene.com' + subtitle_link['href'])
                zip_path = '/home/jevgenij/Downloads/subtitle.zip'
                with open(zip_path, 'wb') as output:
                    output.write(subtitle_response.content)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('.')

                raise SystemExit

