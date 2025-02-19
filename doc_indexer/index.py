import string
import re
import os
import subprocess
import sys
import argparse
import yaml
from engine.engine import Engine

def recursive(doc_type):
    docs = []
    for root, dirs, files in os.walk(target_path):
        for file in files:
            path = os.path.join(root,file)
            if path.endswith(doc_type):
                docs.append(path)
    return docs

def index_pdf(engine, path, title):
    content = []
    printable = set(string.printable)
    for line in subprocess.check_output(f"pdftotext '{path}' -|perl -0pe 's/([^\\n])\\n([^\\n])/\\1 \\2/g;'", shell=True).decode('UTF-8').split('\n'):
        if re.match(r'.*[A-z]+.*', line) and len(line) >= 1:
            content.append(''.join(filter(lambda x: x in printable, line)))
    if not title:
        title = os.path.basename(path)
    engine.index_doc(title, '\n'.join(content), path)

def index_text(engine, path, title):
    content = []
    printable = set(string.printable)
    with open(path, 'r') as f:
        for line in f.readlines():
            if re.match(r'.*[A-z]+.*', line) and len(line) >= min:
                content.append(''.join(filter(lambda x: x in printable, line)))
    if not title:
        title = os.path.basename(path)
    engine.index_doc(title, '\n'.join(content), path)



def parse_args():
    parser = argparse.ArgumentParser(
                    prog='Doc Indexer')
    parser.add_argument('--title', help="Title of the document. If empty filename=title with textfile.", required=False)
    parser.add_argument('--path', help="Path to file", required=True)
    return parser.parse_args()

if __name__=="__main__":
    args = parse_args()
    e = Engine({"index_dir": "whoosh_doc_index"})
    if args.path.endswith('.pdf'):
        index_pdf(e, args.path, args.title)
    else:
        index_text(e, args.path, args.title)
