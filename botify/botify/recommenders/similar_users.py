import random

from .contextual import Contextual
from .recommender import Recommender
from .sticky_artist import StickyArtist
from .toppop import TopPop


class SimilarUsers(Recommender):
    count_for_special_recommenders = 5

    def __init__(self,
                 tracks_redis,
                 top_tracks_redis,
                 artists_redis,
                 recommendations_for_users_redis,
                 unfavorites_tracks_redis,
                 count_of_bad_recommendations_redis,
                 catalog):
        self.sticky_artists = StickyArtist(tracks_redis, artists_redis, catalog)
        self.fallback_2 = Contextual(tracks_redis, catalog)
        self.tracks_redis = tracks_redis
        self.top_tracks_redis = top_tracks_redis
        self.recommendations_for_users_redis = recommendations_for_users_redis
        self.unfavorites_tracks_redis = unfavorites_tracks_redis
        self.count_of_bad_recommendations_redis = count_of_bad_recommendations_redis
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if prev_track_time <= 0.2:
            count_of_prev_bad_recs = self.count_of_bad_recommendations_redis.get(user)
            if count_of_prev_bad_recs is None:
                count_of_prev_bad_recs = 1
            else:
                count_of_prev_bad_recs = int(count_of_prev_bad_recs) + 1

            if count_of_prev_bad_recs == 5:
                self.count_of_bad_recommendations_redis.set(user, 0)
                return self.special_recommendations(user, prev_track, prev_track_time)
            else:
                self.count_of_bad_recommendations_redis.set(user, count_of_prev_bad_recs)
        else:
            self.count_of_bad_recommendations_redis.set(user, 0)

        return self.check_for_unfavorite(
            self.sticky_artists.recommend_next(user, prev_track, prev_track_time),
            user, prev_track, prev_track_time)

    def check_for_unfavorite(self, track, user, prev_track, prev_track_time):
        unfavorites_tracks = self.unfavorites_tracks_redis.get(user)
        if unfavorites_tracks is None or not unfavorites_tracks:
            return track
        else:
            unfavorites_tracks = self.catalog.from_bytes(unfavorites_tracks)
            if track in unfavorites_tracks[:3]:
                return self.special_recommendations(user, prev_track, prev_track_time)
            else:
                return track

    def special_recommendations(self, user, prev_track, prev_track_time):
        return self.fallback_2.recommend_next(user, prev_track, prev_track_time)
