import re
import movie_info


def extract_movie_info(filename: str):
    quality_patterns = {'bluray', 'bdrip', 'hdrip', 'dvdrip', 'web-dl', 'dvdscr', 'web[^\-]', 'webrip'}
    resolution_patterns = {'720p', '1080p'}

    (title, year) = _extract_title_year_from_filename(filename)
    episode_matches = re.search(r's\d\de\d\d', filename, flags=re.IGNORECASE)
    quality_matches = re.search(r'\b(' + '|'.join(quality_patterns) + r')\b', filename, flags=re.IGNORECASE)
    resolution_matches = re.search(r'\b(' + '|'.join(resolution_patterns) + r')\b', filename, flags=re.IGNORECASE)
    filtered_filename = re.sub(r'\[.+\]', '', filename)
    group_matches = re.search(r'-(\w+)(\.\w{3})?$', filtered_filename)

    return movie_info.MovieInfo(
        filename,
        title,
        episode_matches[0] if episode_matches else None,
        quality_matches[1] if quality_matches else "",
        resolution_matches[0] if resolution_matches else "",
        group_matches[1] if group_matches else "",
        year
    )


def _extract_title_year_from_filename(filename: str) -> tuple:
    """Returns a tuple where the first element is movie title with spaces and the second one is year.
    The year is not available for series, in that case the second value is None.
    """
    matches = re.match(r'(.+)(2\d{3})', filename)
    if matches:
        return _add_single_quotes(matches[1].replace('.', ' ')).strip(), matches[2]

    series_matches = re.match(r'(.+)s\d\de\d\d', filename, flags=re.IGNORECASE)
    if series_matches:
        return _add_single_quotes(series_matches[1].replace('.', ' ')).strip(), None

    return _add_single_quotes(filename.replace('.', ' ')).strip(), None


def _add_single_quotes(title: str) -> str:
    return re.sub(
        r'(is|are|was|were|have|has|had|do|does|did|could|should|wo|would)nt',
        '\g<1>n\'t',
        title
    ).replace('cant', "can't")
