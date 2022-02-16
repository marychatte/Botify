from .random import Random
from .recommender import Recommender


class TopPop(Recommender):
    def __init__(self, tracks_redis):
        self.random = Random(tracks_redis)

    # TODO 2: Implement TopPop recommender
    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        return self.random.recommend_next(user, prev_track, prev_track_time)
