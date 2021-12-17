import os
import re
import time
import urllib
import zipfile

import requests

import html_fetcher
import movie_info
from movie_info_extracter import extract_movie_info


def download(movie: movie_info.MovieInfo):
    search_html = html_fetcher.fetch_post(
        'https://subscene.com/subtitles/searchbytitle',
        {'query': urllib.parse.quote_plus(movie.title), 'l': ''}
    )
    if search_html is None:
        return False
    # this might be giving too many results, having the check below in mind
    result_links = search_html.select('.exact + ul .title a')
    # XXX for series add a map of season number to textual representation and use it to filter the correct title
    if len(result_links) == 0:
        print('Found no exact result links, looking for non-exact matches')
        result_links = search_html.find_all("a", text=re.compile(" \\(" + str(movie.year) + "\\)"))
    else:
        print('Found ' + str(len(result_links)) + ' exact result links')

    for result_link in result_links:
        if movie.year is None or movie.year in result_link.string or str(int(movie.year) - 1) in result_link.string:
            print('Found a suitable result link: ' + result_link.string)
            time.sleep(3)
            list_html = html_fetcher.fetch_get('https://subscene.com' + result_link['href'])
            if list_html is None:
                return False
            subtitle_spans = list_html.select('.language-filter + table .a1 span:nth-child(2)')
            max_similarity_span = None
            max_similarity = 0
            for subtitle_span in subtitle_spans:
                entry_release_info = extract_movie_info(subtitle_span.string.strip())
                entry_similarity = movie.compare(entry_release_info)
                if entry_similarity > max_similarity:
                    max_similarity_span = subtitle_span
                    max_similarity = entry_similarity
                    if max_similarity == 100:
                        break

            if max_similarity_span:
                print('Downloading ' + max_similarity_span.string.strip() + ' (similarity: ' + str(max_similarity) + ')')
                subtitle_link = max_similarity_span.find_parent('a')

                time.sleep(3)
                subtitle_html = html_fetcher.fetch_get('https://subscene.com' + subtitle_link['href'])
                if subtitle_html is None:
                    return False
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
                zip_path = './subtitle.zip'
                with open(zip_path, 'wb') as output:
                    output.write(subtitle_response.content)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('.')

                os.remove(zip_path)

                return True

    return False
