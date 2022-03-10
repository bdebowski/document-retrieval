import argparse

from lib.preprocessing import TextProcessor


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-filename", default="documents.txt")
    parser.add_argument("-o", "--output-filename", default="documents.processed")
    return parser.parse_args()


def main(args):
    """
    Will run preprocessing wherein the following occurs:
        - Read in all the articles/documents
        - tokenize, remove numbers, punctuation, and stop words, normalize, and stem
        - Save articles to new file
    """
    processor = TextProcessor()
    with open(args.input_filename, 'r') as ifs, open(args.output_filename, 'w') as ofs:
        line_num = 0
        for line in ifs:
            processed = processor.process(line)
            if processed:
                ofs.write(processed + '\n')
            line_num += 1
            if line_num % 10000 == 0:
                print("Processed {} lines".format(line_num))


if __name__ == "__main__":
    main(parse_args())
