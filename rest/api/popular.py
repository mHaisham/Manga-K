from flask_api import status
from flask_restful import Resource

from network.scrapers import Mangakakalot
from rest.encoding import manga_link
from rest.error import error_message


class Popular(Resource):
    def get(self, i=1):

        mangakakalot = Mangakakalot()
        mangas = mangakakalot.get_popular(i)

        if mangas is None:
            return error_message(f'Popular at index {i} not found'), status.HTTP_404_NOT_FOUND

        popular = []
        for manga in mangas:
            d_manga = vars(manga)

            del d_manga['description']
            del d_manga['status']

            d_manga['link'] = manga_link(manga.title)

            popular.append(d_manga)

        return popular