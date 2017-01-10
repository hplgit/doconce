from builtins import str
from publish import config
_format_venue = config.formatting._format_venue
from publish.common import short_author
from publish.config.defaults import thesistype_strings
import re

#------------------------------------------------------------------------------
# DocOnce formatting
#------------------------------------------------------------------------------

def doconce_format_articles(paper):
    "Return string for article in DocOnce format"
    values = []

    # Key
    values.append(_doconce_get_key_string(paper))

    # Author
    values.append(_doconce_get_authors_string(paper["author"]))

    # Title
    values.append(_doconce_format_title(paper))

    # Journal
    formatted_venue = '*%s*' % \
         _format_venue(paper["journal"], paper["journal"], paper)

    values.append(formatted_venue)

    # Volume
    if "volume" in paper:
        vol = paper["volume"]
        if "number" in paper :
            vol += "(%s)" % paper["number"]
        values.append(vol)

    # Pages
    if "pages" in paper:
        values.append(_doconce_format_pages(paper["pages"]))

    # DOI
    if "doi" in paper:
        values.append(_doconce_format_doi(paper["doi"]))

    # arXiv
    if "arxiv" in paper:
        values.append(_doconce_format_arxiv(paper["arxiv"]))

    # Year
    if "year" in paper:
        values.append(paper["year"])

    if "note" in paper:
        values.append(_doconce_format_note(paper["note"]))

    # How published/URL
    values = _doconce_url(paper, values)

    # About sequence of URL vs year: For publications where howpublished
    # or URL is unusual, this info is placed last (articles, books, misc,
    # posters, theses, proceedings, chapters, edited books),
    # while for publications where howpublished/url is likely, it
    # is placed before year (talks, courses, manual, reports).

    return _doconce_join(values)

def doconce_format_books(paper):
    "Return string for book in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append('*%s*' % _doconce_format_title(paper))
    if "edition" in paper:
        values.append(_doconce_format_edition(paper))
    if "series" in paper:
        values.append(_doconce_format_bookseries(paper))
    if "publisher" in paper:
        values.append(paper["publisher"])
    values.append(paper["year"])
    if "doi" in paper: values.append(_doconce_format_doi(paper["doi"]))
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def doconce_format_edited(paper):
    "Return string for edited book in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "publisher" in paper:
        values.append(paper["publisher"])
    values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def doconce_format_chapters(paper):
    "Return string for chapter in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    values.append(paper["booktitle"])
    values.append(_doconce_format_editors(paper))
    if "publisher" in paper:
        values.append(paper["publisher"])
    if "chapter" in paper:
        values.append("Chapter %s" % paper["chapter"])
    if "pages" in paper:
        values.append("pp. %s" % _doconce_format_pages(paper["pages"]))
    values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def doconce_format_proceedings(paper):
    "Return string for proceeding in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    values.append(_doconce_format_booktitle(paper))
    if "editor" in paper: values.append(_doconce_format_editors(paper))
    if "publisher" in paper: values.append(paper["publisher"])
    values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def doconce_format_reports(paper):
    "Return string for report in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "institution" in paper: values.append(_doconce_format_institution(paper))
    if "number" in paper: values.append(paper["number"])
    values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def doconce_format_manuals(paper):
    "Return string for manual in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    values = _doconce_url(paper, values)
    if "year" in paper: values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def doconce_format_theses(paper):
    "Return string for thesis in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    values.append(thesistype_strings[paper["thesistype"]])
    if "school" in paper: values.append(paper["school"])
    values = _doconce_url(paper, values)
    values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def doconce_format_courses(paper):
    "Return string for course in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "institution" in paper: values.append(_doconce_format_institution(paper))
    values = _doconce_url(paper, values)
    if "year" in paper: values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def doconce_format_talks(paper):
    "Return string for talk in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values = _doconce_url(paper, values)
    values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def doconce_format_posters(paper):
    "Return string for poster in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)


def doconce_format_misc(paper):
    "Return string for misc in DocOnce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    if "author" in paper:
        values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "booktitle" in paper: values.append("in *%s*" % paper["booktitle"])
    if "meeting" in paper: values.append(paper["meeting"])
    if "thesistype" in paper: values.append(thesistype_strings[paper["thesistype"]])
    if "school" in paper: values.append(paper["school"])
    if "chapter" in paper: values.append("Chapter %s" % paper["chapter"])
    if "volume" in paper: values.append("vol. %s" % paper["volume"])
    if "pages" in paper: values.append("pp. %s" % _doconce_format_pages(paper["pages"]))
    if "year" in paper: values.append(paper["year"])
    if "note" in paper: values.append(_doconce_format_note(paper["note"]))
    values = _doconce_url(paper, values)
    return _doconce_join(values)

def _doconce_format_note(note):
    # Make sure \url is handled correctly, LaTeX needs URLs this way
    pattern = r'\\url\{(.+?)\}'
    m = re.search(pattern, note)
    if m:
        note = re.sub(pattern, 'URL: "\g<1>"', note)
    return note

def _doconce_url(paper, values):
    venue = None
    if "howpublished" in paper:
        venue = paper["howpublished"]
        if venue.startswith('\\url{') and venue.endswith('}'):
            venue = venue[5:-1]
        if venue.startswith('http'):
            venue = _doconce_format_url(venue)
        values.append(venue)
    if "url" in paper:
        if "note" in paper:
            if (paper["url"] not in paper["note"]) and \
               (paper["url"] not in paper["howpublished"]):
                values.append(_doconce_format_url(paper["url"]))
        else:
            values.append(_doconce_format_url(paper["url"]))
    return values

def _doconce_get_key_string(paper):
    return 'label{%s}' % paper["key"]

def _doconce_format_title(paper):
    "Format title for DocOnce, with or without link to PDF file"
    if paper["category"] == "courses":
        title = "%s (%s)" % (paper["title"], paper["code"])
    else:
        title = paper["title"]
    #return "*%s*" % title
    return title

def _doconce_format_booktitle(paper):
    return '*%s*' % paper["booktitle"]

def _doconce_format_edition(paper):
    return paper["edition"].lower() + ' edition'

def _doconce_format_bookseries(paper):
    return '*%s*' % paper["series"]

def _doconce_format_editors(paper):
    "Convert editor tuple to author string"
    return "edited by %s" % _doconce_get_authors_string(paper["editor"])

def _doconce_get_authors_string(authors):
    "Convert author tuple to author string"
    authors = [_doconce_mark_author(author, short_author(author).strip()) \
                   for author in authors]
    if len(authors) == 1:
        str = authors[0]
    else :
        if authors[-1] == "others":
            str =  ", ".join(authors[:-1]) + " et al."
        else:
            str = ", ".join(authors[:-1]) + " and " + authors[-1]
    #str = "_%s (%s)_" % (str, paper["year"])
    str = "_%s_" % (str)
    return str

def _doconce_mark_author(author, text) :
  "Mark the text with bold face if author is in the list of marked authors"
  if config.has_key("mark_author") and author.strip() in config.get("mark_author") :
    return "_%s_" % text
  else:
    return text

def _doconce_format_pages(pages):
    "Format pages"
    if "--" in pages:
        pages = pages.replace("--", "-")
    return "pp. %s" % pages

def _doconce_format_institution(paper):
    return '*%s*' % paper["institution"]

def _doconce_format_doi(doi):
    "Format DOI"
    return '"doi: %s": "http://dx.doi.org/%s"' % (doi, doi)

def _doconce_format_arxiv(arxiv):
    "Format arXiv"
    return '"arXiv: %s": "http://arxiv.org/abs/%s"' % (arxiv, arxiv)

def _doconce_format_url(url):
    "Format URL"
    if url.startswith('\\url{'):
        url = url[5:-1]
    if url.startswith('\\emph{'):
        url = url[6:-1]
    return 'URL: "%s"' % (url)

def _doconce_join(values):
    "Join values for DocOnce entry"
    entry = values[1] + ". \n    " + ",\n    ".join(values[2:]) + "." + "\n"
    entry = entry.replace("{", "")
    entry = entry.replace("}", "")
    entry = entry.replace("\\&", "&")
    entry = "  o " + values[0] + " " + entry
    return entry

doconce_format = {
    "articles"      : doconce_format_articles,
    "books"         : doconce_format_books,
    "edited"        : doconce_format_edited,
    "chapters"      : doconce_format_chapters,
    "proceedings"   : doconce_format_proceedings,
    "refproceedings": doconce_format_proceedings,
    "reports"       : doconce_format_reports,
    "manuals"       : doconce_format_manuals,
    "theses"        : doconce_format_theses,
    "courses"       : doconce_format_courses,
    "talks"         : doconce_format_talks,
    "posters"       : doconce_format_posters,
    "misc"          : doconce_format_misc}


#------------------------------------------------------------------------------
# reST formatting
#------------------------------------------------------------------------------

def rst_format_articles(paper):
    "Return string for article in reST format"
    values = []

    # Key
    values.append(_rst_get_key_string(paper))

    # Author
    values.append(_rst_get_authors_string(paper["author"]))

    # Title
    values.append(_rst_format_title(paper))

    # Journal
    try:
        formatted_venue = '*%s*' % \
           _format_venue(paper["journal"], paper["journal"], paper)
    except KeyError as e:
        raise ValueError('publish entry: %s\nmissing field: %s'
                         % (str(paper), str(e)))

    values.append(formatted_venue)

    # Volume
    if "volume" in paper:
        vol = paper["volume"]
        if "number" in paper :
            vol += "(%s)" % paper["number"]
        values.append(vol)

    # Pages
    if "pages" in paper:
        values.append(_rst_format_pages(paper["pages"]))

    # DOI
    if "doi" in paper:
        values.append(_rst_format_doi(paper["doi"]))

    # arXiv
    if "arxiv" in paper:
        values.append(_rst_format_arxiv(paper["arxiv"]))

    # Year
    if "year" in paper:
        values.append(paper["year"])

    # Note
    if "note" in paper:
        values.append(_rst_format_note(paper["note"]))

    # URL/howpublished
    values = _rst_url(paper, values)

    return _rst_join(values)

def rst_format_books(paper):
    "Return string for book in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append('*%s*' % _rst_format_title(paper))
    if "edition" in paper:
        values.append(_rst_format_edition(paper))
    if "series" in paper:
        values.append(_rst_format_bookseries(paper))
    if "publisher" in paper:
        values.append(paper["publisher"])
    values.append(paper["year"])
    if "doi" in paper: values.append(_rst_format_doi(paper["doi"]))
    values = _rst_url(paper, values)
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def rst_format_edited(paper):
    "Return string for edited book in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "publisher" in paper:
        values.append(paper["publisher"])
    values.append(paper["year"])
    values = _rst_url(paper, values)
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def rst_format_chapters(paper):
    "Return string for chapter in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    values.append(paper["booktitle"])
    values.append(_rst_format_editors(paper))
    if "publisher" in paper:
        values.append(paper["publisher"])
    if "chapter" in paper: values.append("Chapter %s" % paper["chapter"])
    if "pages" in paper: values.append("pp. %s" % _rst_format_pages(paper["pages"]))
    values.append(paper["year"])
    values = _rst_url(paper, values)
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def rst_format_proceedings(paper):
    "Return string for proceedings in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    values.append(paper["booktitle"])
    if "editor" in paper: values.append(_rst_format_editors(paper))
    if "publisher" in paper: values.append(paper["publisher"])
    values.append(paper["year"])
    values = _rst_url(paper, values)
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def rst_format_reports(paper):
    "Return string for report in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "institution" in paper: values.append(_rst_format_institution(paper))
    if "number" in paper: values.append(paper["number"])
    values = _rst_url(paper, values)
    if "year" in paper: values.append(paper["year"])
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def rst_format_manuals(paper):
    "Return string for manual in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    values = _rst_url(paper, values)
    if "year" in paper: values.append(paper["year"])
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def rst_format_theses(paper):
    "Return string for thesis in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    values.append(thesistype_strings[paper["thesistype"]])
    values.append(paper["school"])
    values.append(paper["year"])
    values = _rst_url(paper, values)
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def rst_format_courses(paper):
    "Return string for course in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "institution" in paper: values.append(_rst_format_institution(paper))
    values = _rst_url(paper, values)
    if "year" in paper: values.append(paper["year"])
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def rst_format_talks(paper):
    "Return string for talk in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values = _rst_url(paper, values)
    values.append(paper["year"])
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def rst_format_posters(paper):
    "Return string for poster in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values.append(paper["year"])
    values = _rst_url(paper, values)
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)


def rst_format_misc(paper):
    "Return string for misc in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    if "author" in paper:
        values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "booktitle" in paper: values.append("in *%s*" % paper["booktitle"])
    if "meeting" in paper: values.append(paper["meeting"])
    if "thesistype" in paper: values.append(thesistype_strings[paper["thesistype"]])
    if "school" in paper: values.append(paper["school"])
    if "chapter" in paper: values.append("Chapter %s" % paper["chapter"])
    if "volume" in paper: values.append("vol. %s" % paper["volume"])
    if "pages" in paper: values.append("pp. %s" % _rst_format_pages(paper["pages"]))
    values = _rst_url(paper, values)
    if "year" in paper: values.append(paper["year"])
    if "note" in paper: values.append(_rst_format_note(paper["note"]))
    return _rst_join(values)

def _rst_format_note(note):
    # Make sure \url is handled correctly, LaTeX needs URLs this way
    pattern = r'\\url\{(.+?)\}'
    m = re.search(pattern, note)
    if m:
        note = re.sub(pattern, 'URL: "\g<1>"', note)
    return note

def _rst_url(paper, values):
    venue = None
    if "howpublished" in paper:
        venue = paper["howpublished"]
        if venue.startswith('\\url{') and venue.endswith('}'):
            venue = venue[5:-1]
        if venue.startswith('http'):
            venue = _rst_format_url(venue)
        values.append(venue)
    if "url" in paper:
        if "note" in paper:
            if (paper["url"] not in paper["note"]) and \
               (paper["url"] not in paper["howpublished"]):
                values.append(_rst_format_url(paper["url"]))
        else:
            values.append(_rst_format_url(paper["url"]))
    return values

def _rst_get_key_string(paper):
    return '[%s]' % paper["key"]

def _rst_format_title(paper):
    "Format title for reST, with or without link to PDF file"
    if paper["category"] == "courses":
        title = "%s (%s)" % (paper["title"], paper["code"])
    else:
        title = paper["title"]
    #return "*%s*" % title
    return title

def _rst_format_edition(paper):
    return paper["edition"].lower() + ' edition'

def _rst_format_bookseries(paper):
    return '*%s*' % paper["series"]

def _rst_format_editors(paper):
    "Convert editor tuple to author string"
    return "edited by %s" % _rst_get_authors_string(paper["editor"])

def _rst_get_authors_string(authors):
    "Convert author tuple to author string"
    authors = [_rst_mark_author(author, short_author(author).strip()) \
                   for author in authors]
    if len(authors) == 1:
        str = authors[0]
    else :
        if authors[-1] == "others":
            str =  ", ".join(authors[:-1]) + " et al."
        else:
            str = ", ".join(authors[:-1]) + " and " + authors[-1]
    #str = "_%s (%s)_" % (str, paper["year"])
    str = "_%s_" % (str)
    return str

def _rst_mark_author(author, text) :
  "Mark the text with bold face if author is in the list of marked authors"
  if config.has_key("mark_author") and author.strip() in config.get("mark_author") :
    return "_%s_" % text
  else:
    return text

def _rst_format_pages(pages):
    "Format pages"
    if "--" in pages:
        pages = pages.replace("--", "-")
    return "pp. %s" % pages

def _rst_format_institution(paper):
    return '*%s*' % paper["institution"]

def _rst_format_doi(doi):
    "Format DOI"
    return '"doi: %s": "http://dx.doi.org/%s"' % (doi, doi)

def _rst_format_arxiv(arxiv):
    "Format arXiv"
    return '"arXiv: %s": "http://arxiv.org/abs/%s"' % (arxiv, arxiv)

def _rst_format_url(url):
    "Format URL"
    return '`%s <%s>`_' % (url, url)

def _rst_join(values):
    "Join values for reST entry"
    entry = ".. " + values[0] + "\n   " + values[1] + ". " + ",\n   ".join(values[2:]) + "." + "\n"
    entry = entry.replace("{", "")
    entry = entry.replace("}", "")
    return entry

rst_format = {
    "articles"      : rst_format_articles,
    "books"         : rst_format_books,
    "edited"        : rst_format_edited,
    "chapters"      : rst_format_chapters,
    "proceedings"   : rst_format_proceedings,
    "refproceedings": rst_format_proceedings,
    "reports"       : rst_format_reports,
    "manuals"       : rst_format_manuals,
    "theses"        : rst_format_theses,
    "courses"       : rst_format_courses,
    "talks"         : rst_format_talks,
    "posters"       : rst_format_posters,
    "misc"          : rst_format_misc}


#------------------------------------------------------------------------------
# XML formatting
#------------------------------------------------------------------------------

def xml_format_articles(paper):
    "Return string for article in XML format"
    values = []

    # Key
    values.append(_xml('key', paper))

    # Author
    values.append(_xml_get_authors_string(paper["author"]))

    # Title
    values.append(_xml_format_title(paper))

    # Journal
    values.append('<journal>%s</journal>' %
                  _format_venue(paper["journal"], paper["journal"], paper))

    for tag in ['volume', 'number', 'pages', 'doi', 'arxiv', 'year', 'url']:
        if tag in paper:
            values.append(_xml(tag, paper))

    return _xml_join(values)

def xml_format_books(paper):
    "Return string for book in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    if "edition" in paper:
        values.append(_xml_format_edition(paper))
    if "series" in paper:
        values.append(_xml_format_bookseries(paper))
    if "publisher" in paper:
        values.append(_xml("publisher", paper))
    values.append(_xml("year", paper))
    if "doi" in paper: values.append(_xml('doi', paper))
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def xml_format_edited(paper):
    "Return string for edited book in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    if "publisher" in paper:
        values.append(paper["publisher"])
    values.append(paper["year"])
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def xml_format_chapters(paper):
    "Return string for chapter in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    values.append(_xml("booktitle", paper))
    values.append(_xml_format_editors(paper))
    if "publisher" in paper:
        values.append(_xml("publisher", paper))
    if "chapter" in paper:
        values.append(_xml("chapter", paper))
    if "pages" in paper:
        values.append(_xml_format_pages(paper["pages"]))
    values.append(_xml('year', paper))
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def xml_format_proceedings(paper):
    "Return string for proceeding in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    values.append(_xml_format_booktitle(paper))
    if "editor" in paper: values.append(_xml_format_editors(paper))
    if "publisher" in paper: values.append(_xml("publisher", paper))
    values.append(_xml("year", paper))
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def xml_format_reports(paper):
    "Return string for report in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    if "institution" in paper: values.append(_xml_format_institution(paper))
    if "number" in paper: values.append(_xml("number", paper))
    values.append(_xml("year", paper))
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def xml_format_manuals(paper):
    "Return string for manual in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    if "year" in paper: values.append(_xml("year", paper))
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def xml_format_theses(paper):
    "Return string for thesis in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    values.append(thesistype_strings[paper["thesistype"]])
    if "school" in paper: values.append(_xml("school", paper))
    values.append(_xml("year", paper))
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def xml_format_courses(paper):
    "Return string for course in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    if "institution" in paper: values.append(_xml('institution', paper))
    if "year" in paper: values.append(_xml('year', paper))
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def xml_format_talks(paper):
    "Return string for talk in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values.append(paper["year"])
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def xml_format_posters(paper):
    "Return string for poster in XML format"
    values = []
    values.append(_xml('key', paper))
    values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values.append(paper["year"])
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)


def xml_format_misc(paper):
    "Return string for misc in XML format"
    values = []
    values.append(_xml('key', paper))
    if "author" in paper:
        values.append(_xml_get_authors_string(paper["author"]))
    values.append(_xml_format_title(paper))
    if "howpublished" in paper:
        howpublished = paper["howpublished"]
        values.append(howpublished)
    if "booktitle" in paper: values.append("in *%s*" % paper["booktitle"])
    if "meeting" in paper: values.append(paper["meeting"])
    if "thesistype" in paper: values.append(thesistype_strings[paper["thesistype"]])
    if "school" in paper: values.append(paper["school"])
    if "chapter" in paper: values.append("Chapter %s" % paper["chapter"])
    if "volume" in paper: values.append("vol. %s" % paper["volume"])
    if "pages" in paper: values.append("pp. %s" % _xml_format_pages(paper["pages"]))
    if "year" in paper: values.append(paper["year"])
    if "url" in paper: values.append(_xml('url', paper))
    return _xml_join(values)

def _xml(key, paper):
    return '<%s>%s</%s>' % (key, paper[key], key)

def _xml_format_title(paper):
    "Format title for XML, with or without link to PDF file"
    if paper["category"] == "courses":
        title = "<title>%s (%s)</title>" % (paper["title"], paper["code"])
    else:
        title = '<title>%s</title>' % paper["title"]
    return title

def _xml_format_institution(paper):
    return '*%s*' % paper["institution"]

def _xml_format_booktitle(paper):
    return '*%s*' % paper["booktitle"]

def _xml_format_edition(paper):
    return paper["edition"].lower() + ' edition'

def _xml_format_bookseries(paper):
    return '*%s*' % paper["series"]

def _xml_format_editors(paper):
    "Convert editor tuple to author string"
    return "edited by %s" % _xml_get_authors_string(paper["editor"])

def _xml_get_authors_string(authors):
    "Convert author tuple to author string"
    authors = [_xml_mark_author(author, short_author(author).strip())
               for author in authors]
    return '\n'.join(authors)

def _xml_mark_author(author, text):
  "Mark the text with bold face if author is in the list of marked authors"
  if config.has_key("mark_author") and author.strip() in config.get("mark_author") :
    return '<author marked="True">%s</author>' % text
  else:
    return '<author marked="False">%s</author>' % text

def _xml_format_pages(pages):
    if "--" in pages:
        pages = pages.replace("--", "-")
    return '<pages>%s</pages>' % pages

def _xml_join(values):
    return '\n' + '\n'.join(values) + '\n'

xml_format = {
    "articles"      : xml_format_articles,
    "books"         : xml_format_books,
    "edited"        : xml_format_edited,
    "chapters"      : xml_format_chapters,
    "proceedings"   : xml_format_proceedings,
    "refproceedings": xml_format_proceedings,
    "reports"       : xml_format_reports,
    "manuals"       : xml_format_manuals,
    "theses"        : xml_format_theses,
    "courses"       : xml_format_courses,
    "talks"         : xml_format_talks,
    "posters"       : xml_format_posters,
    "misc"          : xml_format_misc}
