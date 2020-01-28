from ..rest import Rest
from .manga import Manga, MangaList
from .favourite import FavouriteList
from .chapter import Chapter

from .search import Search
from .popular import Popular
from .latest import Latest


def setup():
    # init
    api = Rest.get().api

    # setup
    api.add_resource(MangaList, '/mangas')
    api.add_resource(FavouriteList, '/favourites')
    api.add_resource(Manga, '/manga/<title>')
    api.add_resource(Chapter, '/manga/<manga_title>/<chapter_title>')

    api.add_resource(Search, '/search/<int:i>')
    api.add_resource(Popular, '/popular', '/popular/<int:i>')
    api.add_resource(Latest, '/latest', '/latest/<int:i>')