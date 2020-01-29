from flask_api import status
from flask_restful import Resource, reqparse

from database.models import ChapterModel
from database.access import DownloadAccess, MangaAccess

from background.models import DownloadModel
from network.scrapers import Mangakakalot

download_access = DownloadAccess()

parser = reqparse.RequestParser()
parser.add_argument('manga_url', required=True)
parser.add_argument('urls', action='append')


class DownloadsList(Resource):
    def get(self):
        downloads = download_access.get_all()

        models = []
        for model in downloads:
            d_model = model.todict()

            del d_model['path']
            del d_model['pages']

            models.append(d_model)

        return models

    def post(self):  # add download
        args = parser.parse_args()

        mangakakalot = Mangakakalot()

        manga_access = MangaAccess.url(args['manga_url'])
        if manga_access is None:
            return dict(message=f'Manga not found in database', url=args['manga_url']), status.HTTP_404_NOT_FOUND

        info = manga_access.get_info()

        models = []
        for url in args['urls']:
            d_chapter = manga_access.get_chapter_by_url(url)

            model = DownloadModel.create(info, d_chapter, mangakakalot.get_page_list(ChapterModel.fromdict(d_chapter)))
            download_access.add(model)

            d_model = model.todict()
            del d_model['path']
            del d_model['pages']

            models.append(d_model)

        return models


class Download(Resource):
    def get(self, i):
        download = download_access.get(i)
        if download is None:
            return dict(message='Model of index does not exist',
                        length=len(download_access.get_all())), status.HTTP_404_NOT_FOUND

        d_model = download.todict()
        del d_model['path']
        del d_model['pages']

        return d_model
