import os
import re
import zipfile

import requests

import html_fetcher
from movie_info import MovieInfo


def download(movie_info: MovieInfo) -> bool:
    """returns False if no subtitles were found or True if they were found and downloaded
        """
    searchable_title = movie_info.title.replace(' ', '+')
    if movie_info.year:
        searchable_title += '+' + str(movie_info.year)

    if movie_info.episode:
        searchable_title += '+' + movie_info.episode

    search_html = html_fetcher.fetch_get(
        'https://www.opensubtitles.org/en/search2/sublanguageid-eng/moviename-' + searchable_title
    )
    if search_html is None:
        return False

    download_rows = search_html.select('.change.expandable')

    if len(download_rows) == 0 and len(search_html.select('#search_results')) == 1:
        # multiple search results
        result_rows = search_html.select("#search_results .change")
        if movie_info.episode:
            # for episodes search for the episode number among the results
            for result_row in result_rows:
                if movie_info.episode.lower() in result_row.text.lower():
                    movie_page_link = result_row.find('a', href=re.compile('idmovie'))
                    search_html = html_fetcher.fetch_get('https://www.opensubtitles.org' + movie_page_link['href'])
                    if search_html is None:
                        return False
                    download_rows = search_html.select('.change.expandable')

        # check if there is an exact match in search results
        if movie_info.year:
            print('Searching for "' +
                  movie_info.title.lower() + ' (' + str(movie_info.year) + ')" exact match in multiple results')
            for result_row in result_rows:
                movie_page_link = result_row.find('a', href=re.compile('idmovie'))
                if movie_info.title.lower() + ' (' + str(movie_info.year) + ')' == movie_page_link.text.lower().replace('\n', ' '):
                    print('Found exact match in multiple results')
                    search_html = html_fetcher.fetch_get('https://www.opensubtitles.org' + movie_page_link['href'])
                    if search_html is None:
                        return False
                    download_rows = search_html.select('.change.expandable')

    if len(download_rows) == 0:
        return False

    download_links = []
    for row_index, download_row in enumerate(download_rows):
        if 'bad' in download_row['class']:
            continue

        release_text = download_row.find_all(
            string=re.compile(movie_info.quality + '.+' + movie_info.group, re.IGNORECASE)
        )
        if not release_text:
            release_text = download_row.find_all(string=re.compile(movie_info.quality, re.IGNORECASE))
        if release_text or movie_info.episode:
            download_link = download_row.find('a', href=re.compile('/en/subtitleserve/sub/'))
            hearing_impaired = download_row.find_all('img', title='Subtitles for hearing impaired')
            foreign_parts_only = download_row.find_all('img', title='Foreign Parts Only')
            if foreign_parts_only:
                continue
            if hearing_impaired:
                download_links.append(download_link['href'])
            else:
                download_links.insert(0, download_link['href'])
        else:
            print("Did not find a suitable release (quality) or episode in row" + str(row_index))

    if download_links:
        print('Download zip from ' + 'https://www.opensubtitles.org' + download_links[0])
        subtitle_response = requests.get(
            'https://www.opensubtitles.org' + download_links[0],
            headers={
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0',
                'referer': 'https://www.opensubtitles.org/en/subtitleserve/sub/11111'
            }
        )

        zip_path = './subtitle.zip'
        with open(zip_path, 'wb') as output:
            output.write(subtitle_response.content)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('.')

        os.remove(zip_path)

        return True

    return False
