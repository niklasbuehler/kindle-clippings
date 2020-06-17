# -*- coding: utf-8 -*-
import collections
import re
from typing import List, Dict, Union

BOUNDARY = u"==========\r\n"


def _get_sections(file_content: str):
    content = file_content.replace(u'\ufeff', u'')
    return content.split(BOUNDARY)


def _get_clip(section: str) -> Union[None, Dict[str, Union[str, int]]]:
# def _get_clip(section: str):
    clip = {}

    lines = [l for l in section.split(u'\r\n') if l]
    if len(lines) != 3:
        return None

    clip['book'] = lines[0]
    match = re.search(r'(\d+)-\d+', lines[1])
    if not match:
        return None
    position = match.group(1)

    clip['position'] = int(position)
    clip['content'] = lines[2]

    return clip


def get_clips_from_text(content: Union[str, bytes]) -> Dict[str, List]:
    if isinstance(content, bytes):
        content = content.decode('utf-8')

    sections = _get_sections(content)

    clips = collections.defaultdict(list)
    for section in sections:
        clip = _get_clip(section)
        if clip:
            clips[clip['book']].append(clip['content'])
            clips[clip['book']].append(str(clip['position']))

    # remove key with empty value
    clips = {k: v for k, v in clips.items() if v}

    return clips

def get_clips_from_file(filename: str) -> Dict[str, List]:
    with open(filename, 'rb') as f:
        content = f.read().decode('utf-8')
    return get_clips_from_text(content)

def generate_markdown(books: Dict[str, List]):
    print("# Kindle Clippings")
    print("")
    print("## Booklist")

    for book in books:
        print("- " + book)
    
    print("")

    for book in books:
        print("## "+ book)

        it = iter(books[book])
        for highlight in it:
            print("> " + highlight)
            print("")
            print("-- " + book + ", pos. " + next(it))
            print("")
        print("")

if __name__ == '__main__':
    clippings = get_clips_from_file(u'clippings.txt')
    generate_markdown(clippings)
