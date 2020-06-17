# -*- coding: utf-8 -*-
import collections
import re
from typing import List, Dict, Union

BOUNDARY = u"==========\r\n"

def remove_chars(s):
    # Replace colons with a hyphen so "A: B" becomes "A - B"
    s = re.sub(" *: *", " - ", s)
    # Remove question marks or ampersands
    s = s.replace("?", "").replace("&", "and")
    # Replace ( ) with a hyphen so "this (text)" becomes "this - text"
    s = re.sub(r"\((.+?)\)", r"- \1", s)

    # Replace Umlauts
    s = s.replace("Ä", "Ae")
    s = s.replace("Ö", "Oe")
    s = s.replace("Ü", "Ue")
    s = s.replace("ä", "ae")
    s = s.replace("ö", "oe")
    s = s.replace("ü", "ue")

    # Delete filename chars tht are not alphanumeric or ; , _ -
    s = re.sub(r"[^a-zA-Z\d\s;,_-]+", "", s)
    # Trim off anything that isn't a word at the start & end
    s = re.sub(r"^\W+|\W+$", "", s)

    # Split
    s = s.split("-")[0]
    s = s.split(",")[0]
    # Replace spaces with -
    s = s.replace(" ", "-")
    s = s.rstrip("-")

    return s

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

def gen_toc(books: Dict[str, List]) -> str:
    toc = "## Booklist\n\n"

    for book in books:
        toc += ("- [" + book + "](" + gen_filename(book) + ".html)\n")
    
    return toc

def gen_book(title: str, book: List) -> str:
    content = "## " + title + "\n"

    it = iter(book)
    for highlight in it:
        content += "\n"
        content += ("> " + highlight)
        content += "\n\n"
        content += ("-- " + title + ", pos. " + next(it))
        content += "\n"

    return content

def gen_index(books: Dict[str, List]) -> str:
    #index = "# Kindle Clippings\n\n"

    index += gen_toc(books)
    index.write("\n")

    for book in books:
        index += gen_book(book, books[book])
        index += "\n"

    return index

def gen_filename(title: str) -> str:
    return remove_chars(title)

def gen_singlepages(books: Dict[str, List]):
    index = open(u"notes/index.md","w+") 
    #index.write("# Kindle Clippings\n\n")
    index.write(gen_toc(books))
    index.close() 

    for book in books:
        filename = gen_filename(book)
        file = open(u"notes/"+filename+".md", "w+")
        file.write(gen_book(book, books[book]))
        file.close()

if __name__ == '__main__':
    clippings = get_clips_from_file(u'clippings.txt')
    #index = gen_index(clippings)
    #print(index)
    gen_singlepages(clippings)
