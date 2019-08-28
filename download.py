import sys
from pathlib import Path

import downloaders.addict7ed as addic7ed
import downloaders.opensubtitles as opensubtitles
import downloaders.subscene as subscene
from movie_info_extracter import extract_movie_info


def find_movie_filename_in_dir(dir_path: str) -> str:
    movie_extensions = {'avi', 'mkv', 'mp4'}
    current_dir = Path(dir_path)
    for entry in current_dir.iterdir():
        if entry.suffix[1:] in movie_extensions:
            return entry.name


directory = sys.argv[1] if len(sys.argv) == 2 else '.'
movie_filename = find_movie_filename_in_dir(directory)
if not movie_filename:
    print('No movie was found in this dir')
    raise SystemExit

movie_info = extract_movie_info(movie_filename)

downloaded_from_addic7ed = False
if movie_info.episode:
    downloaded_from_addic7ed = addic7ed.download(movie_info)

if downloaded_from_addic7ed:
    raise SystemExit

if movie_info.episode and ' and ' in movie_info.title:
    downloaded_from_addic7ed = addic7ed.download(movie_info)

if downloaded_from_addic7ed:
    raise SystemExit

downloaded_from_opensubtitles = opensubtitles.download(movie_info)
if downloaded_from_opensubtitles:
    raise SystemExit

subscene.download(movie_info)

