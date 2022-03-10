from collections import namedtuple
from typing import IO


DocumentInfo = namedtuple("DocumentInfo", ["doc_id", "title", "text_start_offset"])


class Indexer:

    LABEL_DOC = "$DOC"
    LABEL_TITLE = "$TITLE"
    LABEL_TEXT = "$TEXT"
    NEWLINE_REPLACE = "__n__"

    @classmethod
    def index_terms(cls, documents_fs: IO, sort: bool = True) -> {str: [[int, int]]}:
        """
        Builds a dictionary of terms and their occurrence counts for each document.  For each term there is a list of (doc_index, occurrence_count)
        pairs.
        """

        # Build the index dictionary
        index = {}
        doc_index = -1
        for line in documents_fs:
            if line.startswith(cls.LABEL_DOC):
                doc_index += 1
                continue
            if line.startswith(cls.LABEL_TITLE) or line.startswith(cls.LABEL_TEXT):
                continue
            terms = line.strip().split(" ")
            for term in terms:
                if term not in index:
                    index[term] = [[doc_index, 1]]
                    continue
                if index[term][-1][0] == doc_index:
                    index[term][-1][1] += 1
                else:
                    index[term].append([doc_index, 1])

        # Sort the dictionary if sorting is requested
        if sort:
            index = {k: v for k, v in sorted(index.items())}

        return index

    @classmethod
    def index_docs(cls, documents_fs: IO) -> [DocumentInfo]:
        """
        Build a list of document information containing document ids, titles, and line-numbers locating the first line of text in each document.
        The index in the list corresponds to the document index as used in the term_index dictionary constructed in index_terms().
        """

        index = []

        doc_id = None
        title = ""
        building_title = False
        line = documents_fs.readline()
        while line:
            if line.startswith(cls.LABEL_DOC):
                doc_id = line.strip().split(" ")[1]
            elif line.startswith(cls.LABEL_TITLE):
                building_title = True
            elif line.startswith(cls.LABEL_TEXT):
                # Once we hit the TEXT LABEL we know we have all the information needed to add the current document info
                # We add it now and reset title info
                index.append((doc_id, title[:-1], documents_fs.tell()))  # title[:-1] will drop the '\n' at the end of the title
                building_title = False
                title = ""
            elif building_title:
                title += line
            line = documents_fs.readline()

        return index

    @staticmethod
    def write_dict(term_index: {str: [[int, int]]}, out_fs: IO):
        """
        Converts the term_index provided into a list of terms and their document frequencies.
        Writes the list to the file stream provided.
        """
        for term, occurrences in term_index.items():
            out_fs.write("{} {}\n".format(term, len(occurrences)))

    @staticmethod
    def write_postings(term_index: {str: [[int, int]]}, out_fs: IO):
        """
        Converts the term_index provided into a list of (document_index, term_frequency) pairs and writes these to the file stream provided.
        """
        for term, occurrences in term_index.items():
            for occurrence in occurrences:
                out_fs.write("{} {}\n".format(occurrence[0], occurrence[1]))

    @classmethod
    def write_docids(cls, docs_index: [DocumentInfo], out_fs: IO):
        """
        Writes out the docs_index to file, putting one (doc_id, title, text_start_offset) triplet on each line.
        Titles are modified such that any '\n' are replaced with the NEWLINE_REPLACE string.
        """
        for doc_id, title, text_start_offset in docs_index:
            out_fs.write("{} {} {}\n".format(doc_id, title.replace('\n', cls.NEWLINE_REPLACE), text_start_offset))
