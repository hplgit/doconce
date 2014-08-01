from publish import config
_format_venue = config.formatting._format_venue
from publish.common import short_author
from publish.config.defaults import thesistype_strings

#------------------------------------------------------------------------------
# Doconce formatting
#------------------------------------------------------------------------------

def doconce_format_articles(paper):
    "Return string for article in Doconce format"
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
        if paper.has_key("number") :
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

    # URL
    if "url" in paper:
        values.append(_doconce_format_url(paper["url"]))

    return _doconce_join(values)

def doconce_format_books(paper):
    "Return string for book in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append('*%s*' % _doconce_format_title(paper))
    values.append(paper["publisher"])
    values.append(paper["year"])
    if "doi" in paper: values.append(_doconce_format_doi(paper["doi"]))
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def doconce_format_edited(paper):
    "Return string for edited book in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    values.append(paper["publisher"])
    values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def doconce_format_chapters(paper):
    "Return string for chapter in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    values.append(paper["booktitle"])
    values.append(_doconce_format_editors(paper))
    values.append(paper["publisher"])
    if "chapter" in paper: values.append("Chapter %s" % paper["chapter"])
    if "pages" in paper: values.append("pp. %s" % _doconce_format_pages(paper["pages"]))
    values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def doconce_format_proceedings(paper):
    "Return string for proceeding in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    values.append(_doconce_format_booktitle(paper))
    if "editor" in paper: values.append(_doconce_format_editors(paper))
    if "publisher" in paper: values.append(paper["publisher"])
    values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def doconce_format_reports(paper):
    "Return string for report in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "institution" in paper: values.append(_doconce_format_institution(paper))
    if "number" in paper: values.append(paper["number"])
    values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def doconce_format_manuals(paper):
    "Return string for manual in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "year" in paper: values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def doconce_format_theses(paper):
    "Return string for thesis in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    values.append(thesistype_strings[paper["thesistype"]])
    if "school" in paper: values.append(paper["school"])
    values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def doconce_format_courses(paper):
    "Return string for course in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "institution" in paper: values.append(_doconce_format_institution(paper))
    if "year" in paper: values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def doconce_format_talks(paper):
    "Return string for talk in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def doconce_format_posters(paper):
    "Return string for poster in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)


def doconce_format_misc(paper):
    "Return string for misc in Doconce format"
    values = []
    values.append(_doconce_get_key_string(paper))
    if "author" in paper:
        values.append(_doconce_get_authors_string(paper["author"]))
    values.append(_doconce_format_title(paper))
    if "howpublished" in paper:
        howpublished = paper["howpublished"]
        values.append(howpublished)
    if "booktitle" in paper: values.append("in *%s*" % paper["booktitle"])
    if "meeting" in paper: values.append(paper["meeting"])
    if "thesistype" in paper: values.append(thesistype_strings[paper["thesistype"]])
    if "school" in paper: values.append(paper["school"])
    if "chapter" in paper: values.append("Chapter %s" % paper["chapter"])
    if "volume" in paper: values.append("vol. %s" % paper["volume"])
    if "pages" in paper: values.append("pp. %s" % _doconce_format_pages(paper["pages"]))
    if "year" in paper: values.append(paper["year"])
    if "url" in paper: values.append(_doconce_format_url(paper["url"]))
    return _doconce_join(values)

def _doconce_get_key_string(paper):
    return 'label{%s}' % paper["key"]

def _doconce_format_title(paper):
    "Format title for Doconce, with or without link to PDF file"
    if paper["category"] == "courses":
        title = "%s (%s)" % (paper["title"], paper["code"])
    else:
        title = paper["title"]
    #return "*%s*" % title
    return title

def _doconce_format_booktitle(paper):
    return '*%s*' % paper["booktitle"]

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
    return 'URL: "%s"' % (url)

def _doconce_join(values):
    "Join values for Doconce entry"
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
    formatted_venue = '*%s*' % \
         _format_venue(paper["journal"], paper["journal"], paper)

    values.append(formatted_venue)

    # Volume
    if "volume" in paper:
        vol = paper["volume"]
        if paper.has_key("number") :
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

    # URL
    if "url" in paper:
        values.append(_rst_format_url(paper["url"]))

    return _rst_join(values)

def rst_format_books(paper):
    "Return string for book in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append('*%s*' % _rst_format_title(paper))
    values.append(paper["publisher"])
    values.append(paper["year"])
    if "doi" in paper: values.append(_rst_format_doi(paper["doi"]))
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
    return _rst_join(values)

def rst_format_edited(paper):
    "Return string for edited book in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    values.append(paper["publisher"])
    values.append(paper["year"])
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
    return _rst_join(values)

def rst_format_chapters(paper):
    "Return string for chapter in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    values.append(paper["booktitle"])
    values.append(_rst_format_editors(paper))
    values.append(paper["publisher"])
    if "chapter" in paper: values.append("Chapter %s" % paper["chapter"])
    if "pages" in paper: values.append("pp. %s" % _rst_format_pages(paper["pages"]))
    values.append(paper["year"])
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
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
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
    return _rst_join(values)

def rst_format_reports(paper):
    "Return string for report in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "institution" in paper: values.append(_rst_format_institution(paper))
    if "number" in paper: values.append(paper["number"])
    values.append(paper["year"])
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
    return _rst_join(values)

def rst_format_manuals(paper):
    "Return string for manual in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "year" in paper: values.append(paper["year"])
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
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
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
    return _rst_join(values)

def rst_format_courses(paper):
    "Return string for course in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "institution" in paper: values.append(_rst_format_institution(paper))
    values.append(paper["year"])
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
    return _rst_join(values)

def rst_format_talks(paper):
    "Return string for talk in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values.append(paper["year"])
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
    return _rst_join(values)

def rst_format_posters(paper):
    "Return string for poster in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "meeting" in paper: values.append(paper["meeting"])
    values.append(paper["year"])
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
    return _rst_join(values)


def rst_format_misc(paper):
    "Return string for misc in reST format"
    values = []
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_key_string(paper))
    values.append(_rst_get_authors_string(paper["author"]))
    values.append(_rst_format_title(paper))
    if "howpublished" in paper:
        howpublished = paper["howpublished"]
        values.append(howpublished)
    if "booktitle" in paper: values.append("in *%s*" % paper["booktitle"])
    if "meeting" in paper: values.append(paper["meeting"])
    if "thesistype" in paper: values.append(thesistype_strings[paper["thesistype"]])
    if "school" in paper: values.append(paper["school"])
    if "chapter" in paper: values.append("Chapter %s" % paper["chapter"])
    if "volume" in paper: values.append("vol. %s" % paper["volume"])
    if "pages" in paper: values.append("pp. %s" % _rst_format_pages(paper["pages"]))
    if "year" in paper: values.append(paper["year"])
    if "url" in paper: values.append(_rst_format_url(paper["url"]))
    return _rst_join(values)

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
