import argparse

from lib.indexing import Indexer


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--documents-filename", default="documents.txt")
    parser.add_argument("-p", "--preprocessed-docs-filename", default="documents.processed")
    return parser.parse_args()


def main(args):
    # Read preprocessed documents
    # For each token, add it to the dictionary and count the number of occurrences across the collection
    # Also for each token, construct a list of pairs of [doc_id, token_freq] indicating how many times the token appears in each document it appears
    # in.
    # For each document, store the ID, Title, and starting line in the original input file.
    # Output the above information in three files: dictionary.txt, postings.txt, and docids.txt
    indexer = Indexer()
    with open(args.documents_filename, 'r') as docs_fs, open(args.preprocessed_docs_filename, 'r') as preprocessed_docs_fs:
        print("Indexing terms...")
        terms_index = indexer.index_terms(preprocessed_docs_fs)

        print("Indexing documents...")
        docs_index = indexer.index_docs(docs_fs)

        with open("dictionary.txt", 'w') as ofs:
            print("Writing dictionary...")
            indexer.write_dict(terms_index, ofs)

        with open("postings.txt", 'w') as ofs:
            print("Writing postings...")
            indexer.write_postings(terms_index, ofs)

        with open("docids.txt", 'w') as ofs:
            print("Writing docids...")
            indexer.write_docids(docs_index, ofs)

    print("Indexing completed")


if __name__ == "__main__":
    main(parse_args())
