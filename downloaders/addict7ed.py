import os
import requests
import html_fetcher
from movie_info import MovieInfo


def download(movie_info: MovieInfo) -> bool:
    """returns False if no subtitles were found or True if they were found and downloaded
    """

    movie_title = movie_info.title
    # some series have year as a part of the title (e.g. Happy! (2017)), so concatenate them in such cases
    if movie_info.year:
        movie_title = movie_title + ' ' + str(movie_info.year)

    search_html = html_fetcher.fetch_get(
        'http://www.addic7ed.com/srch.php?search=' + movie_title.replace(' ', '+') + '+' + movie_info.episode +
        '&Submit=Search'
    )

    if search_html is None:
        return False

    # we might have multiple results, so if so, one more click is needed
    if search_html.find('title').text.strip().startswith('Search'):
        result_links = search_html.find_all('a', debug=True)
        if not result_links:
            return False

        # for now we simply take first link, but if needed, look for most suitable title like below
        # for result_link in result_links:
        #     comparable_title = re.sub(r'\s+\-\s.+$', '', result_link.text)

        search_html = html_fetcher.fetch_get('http://www.addic7ed.com/' + result_links[0]['href'])
        if search_html is None:
            return False

    download_links = search_html.select('.buttonDownload')
    matching_download_link = None
    english_download_link = None
    if len(download_links) > 0:
        for download_link in download_links:
            lang_container = download_link.parent.find_previous_sibling('td', 'language')
            group_container = download_link.find_parent('table').find('tr').find('td', 'NewsTitle')
            if lang_container.text.strip() == 'English' and \
                    movie_info.group and group_container.text.lower().find(movie_info.group.lower()) != -1:
                matching_download_link = download_link
                print('Found group match for ' + movie_info.group)
                break
            elif lang_container.text.strip() == 'English':
                english_download_link = download_link

        if english_download_link and not matching_download_link:
            print(f'No group match for {movie_info.group}, taking first English match')
            matching_download_link = english_download_link

        if matching_download_link:
            print('Downloading ' + 'http://www.addic7ed.com' + matching_download_link['href'])

            subtitle_response = requests.get(
                'http://www.addic7ed.com' + matching_download_link['href'],
                headers={'referer': 'http://www.addic7ed.com'}
            )
            print(subtitle_response.status_code)
            subtitle_path = './' + os.path.splitext(movie_info.filename)[0] + '.srt'
            with open(subtitle_path, 'wb') as output:
                output.write(subtitle_response.content)

            return True

    return False
