from typing import IO
from collections import defaultdict
import math

from lib.preprocessing import TextProcessor
from lib.indexing import Indexer, DocumentInfo


class Engine:
    """Performs the search queries"""

    def __init__(self, num_docs: int, dictionary: {str: (int, int)}, postings: [(int, int)], text_processor: TextProcessor, normalize_scores=True):
        """
        :param num_docs: Total number of documents in the collection.
        :param dictionary: A dict of terms where each term maps to a (doc_freq, offset) tuple.  The offset indicates the index in the postings list
            where this term begins.
        :param postings: A list of (doc_index, term_freq) tuples.
        :param text_processor: The text processor which will be used to process the queries.  We want the queries to be processed the same way as the
            documents would have been.
        """

        self._num_docs = num_docs
        self._doc_freqs = {term: val[0] for term, val in dictionary.items()}
        self._offsets = {term: val[1] for term, val in dictionary.items()}
        self._postings_doc_indices = [post[0] for post in postings]
        self._postings_term_freqs = [post[1] for post in postings]
        self._text_processor = text_processor
        self._normalize = normalize_scores

    def retrieve_matches(self, query: str) -> [(int, float)]:
        """
        Retrieves a list of matching document indices and their match score.  The list is sorted in descending order of match score.
        """

        # Get the individual terms in the query and count their frequency
        query_term_freqs = defaultdict(int)
        for term in self._text_processor.process(query).split(' '):
            query_term_freqs[term] += 1

        # For each term in the query we compute the tfidf weight.
        # We also compute the tfidf weight for each term/document intersection.

        # Create a list of (doc_index, similarity) pairs with similarity initialized to 0
        similarities = [[i, 0.0] for i in range(self._num_docs)]
        # Create a variable for the query and each document in which to accumulate the sum of squares of weights for normalization
        sum_square_weights_q = 0.0
        sum_square_weights_docs = [0.0] * self._num_docs
        for term in query_term_freqs:
            # Each term uses an idf value which is common to the query and each document/term intersection, so we compute it once and reuse it.
            idf = math.log2(self._num_docs / self._doc_freqs[term])
            # Compute the term tfidf value for the query: w_qterm
            w_qterm = query_term_freqs[term] * idf
            sum_square_weights_q += w_qterm ** 2.0
            offset = self._offsets[term]
            for doc_index in range(self._num_docs):
                # The tfidf for documents that don't contain the term is 0, so we can just ignore them
                if self._postings_doc_indices[offset] == doc_index:
                    # Compute the term tfidf value for the document: w_dterm
                    # Add to the similarity value for the document the q_term x d_term
                    w_dterm = self._postings_term_freqs[offset] * idf
                    similarities[doc_index][1] += w_qterm * w_dterm
                    sum_square_weights_docs[doc_index] += w_dterm ** 2.0
                    offset += 1

        # Normalize the similarities
        if self._normalize:
            for doc_index in range(self._num_docs):
                if similarities[doc_index][1] > 0.0:
                    similarities[doc_index][1] /= math.sqrt(sum_square_weights_q * sum_square_weights_docs[doc_index])

        # Sort the results
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities


class DocumentDB:
    """
    Stores the document meta-data (ids and titles) and handles retrieval of the document full-text from disk.
    """

    def __init__(self, doc_info: [DocumentInfo], docs_fs: IO):
        self._doc_info = doc_info
        self._docs_fs = docs_fs
        self._doc_text_start_by_id = {info.doc_id: info.text_start_offset for info in doc_info}

    def get_doc_id_and_title(self, doc_index: int) -> (str, str):
        """
        Returns the document id code and title for the given document index.
        """
        return self._doc_info[doc_index].doc_id, self._doc_info[doc_index].title

    def get_doc_text(self, doc_id: str) -> str:
        """
        Returns the whole text of the document retrieved by document id code.
        """
        doc_text = ""
        self._docs_fs.seek(self._doc_text_start_by_id[doc_id])
        for line in self._docs_fs:
            if line.startswith("$DOC"):
                break
            doc_text += line
        return doc_text


def build_engine_from_filepaths(dictionary_file_path, postings_file_path, normalize_scores) -> Engine:
    """
    Builds an Engine object from the dictionary file and postings file specified.
    """

    # Build the dictionary of terms and (document-frequency, offset) pairs.
    # The offsets are derived from the document frequency of each term (and the previous offset); each offset indicates the index in the postings
    # file/list where the corresponding term begins.
    with open(dictionary_file_path, 'r') as fs:
        dictionary = {}
        offset = 0
        for line in fs:
            if not line:
                break
            term, count = line.strip().split(' ')
            count = int(count)
            dictionary[term] = (count, offset)
            offset += count

    # Build the postings list of (doc_index, term_freq) pairs
    with open(postings_file_path, 'r') as fs:
        postings = [(int(line.strip().split(' ')[0]), int(line.strip().split(' ')[1])) for line in fs if line]

    # To count the number of documents in the collection, we create a set and add to it each document index, then get the size of the set
    doc_indices = set()
    for doc_index, term_freq in postings:
        doc_indices.add(doc_index)

    return Engine(len(doc_indices), dictionary, postings, TextProcessor(), normalize_scores)


def build_documents_db_from_file_paths(docids_file_path, documents_file_path) -> DocumentDB:
    """
    Build a DocumentDB object from the docids file and the documents file specified.
    """

    # Build the list of DocumentInfo tuples
    with open(docids_file_path, 'r') as fs:
        doc_info = []
        for line in fs:
            if not line:
                break
            space_split = line.strip().split(' ')
            doc_id = space_split[0]
            text_start_offset = int(space_split[-1])
            title = ' '.join(space_split[1:-1])
            title = title.replace(Indexer.NEWLINE_REPLACE, '\n')
            doc_info.append(DocumentInfo(doc_id, title, text_start_offset))

    # Open the file stream for the documents file
    docs_fs = open(documents_file_path, 'r')

    return DocumentDB(doc_info, docs_fs)
