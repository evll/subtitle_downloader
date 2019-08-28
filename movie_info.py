from __future__ import annotations
from dataclasses import dataclass
import typing


@dataclass
class MovieInfo:
    title: str
    episode: typing.Optional[str]  # available for series only
    quality: str
    resolution: str
    group: str
    year: typing.Optional[int]  # not available for series

    def compare(self, other_movie_info: MovieInfo) -> int:
        """
        :return: Similarity percentage, max 100, min 0
        """
        if self.episode:
            weights = {"episode": 50, "quality": 30, "group": 15, "resolution": 5}
        else:
            weights = {"quality": 70, "group": 20, "resolution": 10}

        similarity = 0
        if self.episode and self.episode.lower() == other_movie_info.episode.lower():
            similarity += weights["episode"]

        if self.quality and self.quality.lower() == other_movie_info.quality.lower():
            similarity += weights["quality"]

        if self.resolution and self.resolution.lower() == other_movie_info.resolution.lower():
            similarity += weights["resolution"]

        if self.group and self.group.lower() == other_movie_info.group.lower():
            similarity += weights["group"]

        return similarity
