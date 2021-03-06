from pathlib import Path

from tinydb import TinyDB

from ..paths import mangas_directory
from ..wrapper.manga import MangaWrapper


class MangaData:
    def __init__(self, base: TinyDB):
        all = base.all()

        # create dict of needed databases
        self.databases = {}
        for entry in all:
            self.add(entry['title'], exists_ok=False)

        # print(self.databases)

    def add(self, title, exists_ok=True):
        if exists_ok:
            if title in self.databases.keys():
                return

        self.databases[title] = MangaWrapper(mangas_directory / Path(f'{title}.db'))

    def all(self):
        return [self.databases[key] for key in self.databases.keys()]