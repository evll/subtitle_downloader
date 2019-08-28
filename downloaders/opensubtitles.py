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

    search_html = html_fetcher.fetch_get(
        'https://www.opensubtitles.org/en/search2?MovieName=' + searchable_title +
        '&id=8&action=search&SubLanguageID=eng&Season=&Episode=&SubSumCD=&Genre=&MovieByteSize=&MovieLanguage=&' +
        'MovieImdbRatingSign=1&MovieImdbRating=&MovieCountry=&MovieYearSign=1&MovieYear=&MovieFPS=&SubFormat=&' +
        'SubAddDate=&Uploader=&IDUser=&Translator=&IMDBID=&MovieHash=&IDMovie='
    )
    # XXX There can be multiple movies found, in this case, take the first match,
    #  see https://www.opensubtitles.org/en/search2/sublanguageid-eng/moviename-aladdin+2019

    download_rows = search_html.select('.change.expandable')

    if len(download_rows) == 0:
        return False

    download_links = []
    for download_row in download_rows:
        release_text = download_row.find_all(string=re.compile(movie_info.quality + '.+' + movie_info.group))
        if not release_text:
            release_text = download_row.find_all(string=re.compile(movie_info.quality))
        if release_text:
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
