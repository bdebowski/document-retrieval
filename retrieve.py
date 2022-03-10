import curses
import argparse

from lib.ui import SearchUI
from lib.retrieval import build_engine_from_filepaths, build_documents_db_from_file_paths


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dictionary-file", "-t", default="dictionary.txt")
    parser.add_argument("--postings-file", "-p", default="postings.txt")
    parser.add_argument("--docids-file", "-i", default="docids.txt")
    parser.add_argument("--documents-file", "-m", default="documents.txt")
    parser.add_argument("--normalize-scores", "-n", action="store_true")
    return parser.parse_args()


def main(stdscr, args):
    """
    Runs the main loop and state machine of the system.
    The user will be prompted to enter a query.  Query results are then displayed and the user can select a result to view the respective document.
    """

    ui = SearchUI(stdscr)
    results_per_page = 10
    engine = build_engine_from_filepaths(args.dictionary_file, args.postings_file, args.normalize_scores)
    docs_db = build_documents_db_from_file_paths(args.docids_file, args.documents_file)

    def build_results(indices_and_scores, page_num):
        def build_result(doc_index, sim_score):
            doc_id, title = docs_db.get_doc_id_and_title(doc_index)
            return sim_score, doc_id, title
        return [build_result(*indices_and_scores[i]) for i in range(page_num * results_per_page, (page_num + 1) * results_per_page)]

    # Main loop
    # We have 3 states organized in a hierarchy: EnterQueryPage->ShowQueryResultsPage->ShowDocumentPage
    while True:
        query = ui.query_page()  # EnterQueryPage state
        if not query:
            return
        indices_and_scores = engine.retrieve_matches(query)
        page_num = 0
        results = build_results(indices_and_scores, page_num)
        while True:
            key = ui.query_results_page(results, query, page_num + 1)  # ShowQueryResultsPage state
            if key == 'q':
                return
            elif key == 'b':
                break
            elif key == 'n':
                page_num += 1
                results = build_results(indices_and_scores, page_num)
            elif key == 'p':
                page_num = max(0, page_num - 1)
                results = build_results(indices_and_scores, page_num)
            else:
                doc_id = results[int(key)][1]
                doc_text = docs_db.get_doc_text(doc_id)
                key = ui.document_page(doc_text)  # ShowDocumentPage state
                if key == 'q':
                    return


if __name__ == "__main__":
    curses.wrapper(main, parse_args())
