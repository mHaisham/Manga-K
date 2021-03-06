import os
import sys
import traceback
from pathlib import Path
from typing import List

from whaaaaat import prompt, Separator

from modules import console
from modules import database
from modules import resource
from modules import resume
from modules import settings
from modules.codec import MKCodec
from modules.commandline import parse
from modules.composition import compose_menu
from modules.console import vinput
from modules.console.menu import Menu
from modules.database import models
from modules.database.models.manga.dialog import MangaDialog
from modules.database.models.manga.download import selective_download
from modules.manager import HtmlManager, MangaManager
from modules.ui import colorize, Loader


def search():
    search = vinput('Enter here to search:')
    url = codec.search_prefix + search
    while True:
        codec.search(url)

        # mutate options to include page routing
        choices: List = codec.search_result[:]
        if codec.previous_page_exists():
            choices.insert(0, 'PREVIOUS')
        if codec.next_page_exists():
            choices.append('NEXT')

        search_answer = Menu('Choose', choices, key=lambda chapter: chapter['name']).prompt()

        if search_answer == 'PREVIOUS':
            url = codec.get_page(codec.current_page - 1)
            continue
        elif search_answer == 'NEXT':
            url = codec.get_page(codec.current_page + 1)
            continue
        else:
            for result in codec.search_result:
                if result['name'] == search_answer:
                    from modules.database.mangas import manga
                    m = models.Manga(result['name'], result['href'])

                    if m.title in manga.databases.keys():
                        info = manga.databases[m.title].get_info()
                        m.is_manhwa = info.is_manhwa

                    return m


def direct():
    answer = vinput('Enter the url: ')

    with Loader("Parse Info"):
        parsed_manga, chapters = models.Manga('', answer).parse()

    return parsed_manga, chapters


def download_link(manga: models.Manga, chapters=None):
    if not chapters:
        manga, chapters = manga.parse()

    exists = manga.title in database.manga.databases.keys()

    if exists:
        with Loader("Update database"):
            # check database and update chapters
            database.manga.databases[manga.title].update_chapter_list(chapters)

            # get new chapters from updated database
            chapters = database.manga.databases[manga.title].get_chapter_list()

    # get settings
    s = settings.get()

    question = {
        'type': 'checkbox',
        'name': 'chapter',
        'message': 'Select chapters to download',
        'choices': [
            dict(name=chapter.title, disabled='Downloaded' if s.disable_downloaded and chapter.downloaded else False)
            for chapter in chapters],
    }

    answers = prompt(question)

    if not answers['chapters']:
        return

    selected = []
    for chapter in chapters:
        if chapter.title in answers['chapters']:
            selected.append(chapter)

    selective_download(manga, chapters, selected, update=not exists)


def continue_downloads():
    manga, unfinished = resume.get()

    if len(unfinished) <= 0:
        return

    # user prompt
    print(
        f'Download of {len(unfinished)} {"chapter" if len(unfinished) == 1 else "chapters"} from "{manga.title}" unfinished.')
    should_resume = console.confirm('Would you like to resume?', default=True)

    if not should_resume:
        # remove all from database and exit
        database.meta.downloads_left.purge()
        return

    # start download
    manga, chapters = manga.parse()
    selective_download(manga, chapters, [models.Chapter.fromdict(chapter) for chapter in unfinished], update=True)


if __name__ == '__main__':
    # set working directory
    os.chdir(str(Path(sys.executable if getattr(sys, 'frozen', False) else __file__).parent))
    models.Manga.mkdir_base()
    resource.manager.check_resources()  # mandatory resource check

    # PLAYGROUND

    # from modules.database.models import Manga
    #
    # v = Manga('name', 'asdas').todict()
    # print(v)
    #
    # input()
    # END

    continue_downloads()

    codec: MKCodec = MKCodec()
    manga_manager: MangaManager = MangaManager()
    html_manager: HtmlManager = HtmlManager()

    # commandline argument parse
    skip_menu, args = parse()

    while True:
        menuoption = {}
        if not skip_menu:
            mainmenu = {
                'type': 'list',
                'name': 'dialog',
                'message': 'what do you wanna do?',
                'choices': [
                    'Search for manga',
                    'Open manga using direct url',
                    'View the manga',
                    Separator('-'),
                    'Compose',
                    'Database',
                    'Settings',
                    'Exit'
                ],
                'filter': lambda val: mainmenu['choices'].index(val)
            }

            menuoption = prompt(mainmenu)
        else:
            if args.view:
                menuoption['dialog'] = 2

        if menuoption['dialog'] == 0:
            try:
                dialog = MangaDialog(search())
                dialog.prompt()
            except Exception:
                traceback.print_exc()
        elif menuoption['dialog'] == 1:
            try:
                manga, chapters = direct()
                dialog = MangaDialog(manga)
                dialog.prompt()
            except Exception:
                traceback.print_exc()
        elif menuoption['dialog'] == 2:
            # generate manga tree
            with Loader('Generating tree'):
                manga_manager.generate_tree()

            # generate html pages using the tree
            with Loader('Generating html files.'):
                html_manager.generate_web(manga_manager.tree)

            if html_manager.open():
                break
        elif menuoption['dialog'] == 4:
            compose_menu()
        elif menuoption['dialog'] == 5:
            database.actions.menu()
        elif menuoption['dialog'] == 6:
            settings.change()
        elif menuoption['dialog'] == 7:
            break
        else:
            print(colorize.red('Pick a valid choice'))
