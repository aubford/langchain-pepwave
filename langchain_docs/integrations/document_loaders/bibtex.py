#!/usr/bin/env python
# coding: utf-8

# # BibTeX
# 
# >[BibTeX](https://www.ctan.org/pkg/bibtex) is a file format and reference management system commonly used in conjunction with `LaTeX` typesetting. It serves as a way to organize and store bibliographic information for academic and research documents.
# 
# `BibTeX` files have a `.bib` extension and consist of plain text entries representing references to various publications, such as books, articles, conference papers, theses, and more. Each `BibTeX` entry follows a specific structure and contains fields for different bibliographic details like author names, publication title, journal or book title, year of publication, page numbers, and more.
# 
# BibTeX files can also store the path to documents, such as `.pdf` files that can be retrieved.

# ## Installation
# First, you need to install `bibtexparser` and `PyMuPDF`.

# In[26]:


get_ipython().run_line_magic('pip', 'install --upgrade --quiet  bibtexparser pymupdf')


# ## Examples

# `BibtexLoader` has these arguments:
# - `file_path`: the path of the `.bib` bibtex file
# - optional `max_docs`: default=None, i.e. not limit. Use it to limit number of retrieved documents.
# - optional `max_content_chars`: default=4000. Use it to limit the number of characters in a single document.
# - optional `load_extra_meta`: default=False. By default only the most important fields from the bibtex entries: `Published` (publication year), `Title`, `Authors`, `Summary`, `Journal`, `Keywords`, and `URL`. If True, it will also try to load return `entry_id`, `note`, `doi`, and `links` fields. 
# - optional `file_pattern`: default=`r'[^:]+\.pdf'`. Regex pattern to find files in the `file` entry. Default pattern supports `Zotero` flavour bibtex style and bare file path.

# In[27]:


from langchain_community.document_loaders import BibtexLoader


# In[28]:


# Create a dummy bibtex file and download a pdf.
import urllib.request

urllib.request.urlretrieve(
    "https://www.fourmilab.ch/etexts/einstein/specrel/specrel.pdf", "einstein1905.pdf"
)

bibtex_text = """
    @article{einstein1915,
        title={Die Feldgleichungen der Gravitation},
        abstract={Die Grundgleichungen der Gravitation, die ich hier entwickeln werde, wurden von mir in einer Abhandlung: ,,Die formale Grundlage der allgemeinen Relativit{\"a}tstheorie`` in den Sitzungsberichten der Preu{\ss}ischen Akademie der Wissenschaften 1915 ver{\"o}ffentlicht.},
        author={Einstein, Albert},
        journal={Sitzungsberichte der K{\"o}niglich Preu{\ss}ischen Akademie der Wissenschaften},
        volume={1915},
        number={1},
        pages={844--847},
        year={1915},
        doi={10.1002/andp.19163540702},
        link={https://onlinelibrary.wiley.com/doi/abs/10.1002/andp.19163540702},
        file={einstein1905.pdf}
    }
    """
# save bibtex_text to biblio.bib file
with open("./biblio.bib", "w") as file:
    file.write(bibtex_text)


# In[29]:


docs = BibtexLoader("./biblio.bib").load()


# In[30]:


docs[0].metadata


# In[31]:


print(docs[0].page_content[:400])  # all pages of the pdf content

