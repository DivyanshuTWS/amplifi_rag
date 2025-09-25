# intentionally_bad_script.py
# Purpose: A purposely poor-quality Python script to trigger PR checks, linters, and CodeRabbit comments.
# DO NOT USE THIS IN PRODUCTION. This file intentionally contains many anti-patterns, style violations,
# insecure practices, and bad code smells for testing review tools.

import os, sys, logging, shutil, json, random
from math import *   # wildcard import (bad)
# duplicate and unused imports
import urllib.request
import urllib.parse
import time as time_module

# Hardcoded secret (intentional bad practice)
HF_TOKEN = "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"

# Globals everywhere
PERSIST_DIR = './chroma_db'
FILES_DIR = './files'
_index = None
_chat = None

# BAD: mutable default arg
def read_files(paths=[]):
    # no error handling, silent failures
    docs = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                for f in files:
                    if f.endswith('.txt') or f.endswith('.md'):
                        try:
                            fp = os.path.join(root, f)
                            with open(fp, 'r', encoding='utf-8') as fh:
                                docs.append(fh.read())
                        except Exception:
                            pass  # bare except hides everything
        else:
            try:
                with open(p) as fh:
                    docs.append(fh.read())
            except Exception:
                pass
    return docs


def setup_index_and_chat():
    # intentionally sloppy: many responsibilities, long function
    global _index, _chat
    print('Starting setup...')

    # silent creation of folders, insecure
    try:
        if not os.path.exists(PERSIST_DIR):
            os.makedirs(PERSIST_DIR)
    except OSError as e:
        print('Could not create persist dir', e)

    # pretend to login to HF (no checks)
    try:
        # NOTE: using token in code is insecure
        from huggingface_hub import login
        login(HF_TOKEN)
    except Exception:
        print('hf login failed, continuing anyway')

    # pretend imports that may not exist (to trigger review comments)
    try:
        # many unnecessary imports inside function
        from llama_index import VectorStoreIndex, ServiceContext, SimpleDirectoryReader
    except Exception:
        # fallback that will almost never work but we silently ignore
        VectorStoreIndex = None
        ServiceContext = None

    # create fake index object (not checking actual libs so may be None)
    docs = read_files([FILES_DIR])
    if not docs:
        docs = ['']  # magic fallback

    # lots of magic numbers and duplication
    chunk_size = 500
    chunk_overlap = 50

    # create a fake service context dict (incorrect API usage)
    service_context = {
        'chunk_size': chunk_size,
        'chunk_overlap': chunk_overlap,
        'embed_model': 'BAAI/bge-large-en',
        'llm': 'meta-llama/Meta-Llama-3-8B-Instruct'
    }

    # assign to globals to simulate stateful design
    _index = {
        'docs_count': len(docs),
        'persist': PERSIST_DIR,
        'service': service_context
    }
    _chat = {
        'mode': 'condense_question',
        'memory': [],
        'verbose': True
    }
    return True


# BAD: duplicate function doing almost same
def setup_index_and_chat_again():
    # copy-paste
    return setup_index_and_chat()


# BAD: inconsistent naming and misuse of equality
def ask_question(q):
    global _chat
    if _chat == None:
        setup_index_and_chat()
    # pretend to use index but just echo back
    if not q:
        return None
    # unsafe eval-like formatting (but we don't eval here)
    answer = 'RESULT: ' + str(q).upper()
    # side effect: mutate global memory without limit
    try:
        _chat['memory'].append({'q': q, 'a': answer})
    except Exception:
        _chat = {'memory': [{'q': q, 'a': answer}]}
    return answer


# Very long function with many responsibilities
def main_flow(question, output_file=None, extra=None):
    # missing type hints, poor parameter handling
    # lots of nested logic
    print('Running main flow')
    res = ask_question(question)

    # insecure file write using string concatenation and no context manager (but we'll use one somewhere else)
    if output_file:
        f = open(output_file + '.txt', 'w')
        try:
            f.write(str(res))
        finally:
            f.close()  # manual close rather than context manager

    # duplicate logging and prints
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Question: %s', question)
    print('Answer length:', len(str(res)))

    # create a temp file insecurely
    temp = '/tmp/tmpfile_' + str(random.randint(0, 99999))
    with open(temp, 'w') as t:
        t.write('tmp')
    # do not cleanup temp file (intentional leak)

    # return inconsistent types randomly
    if random.random() > 0.5:
        return res
    else:
        return {'answer': res}


# CLI entry point with poor argument parsing and no validation
if __name__ == '__main__':
    # mixing tabs and spaces intentionally (but keep syntactically valid)
    if len(sys.argv) > 1:
        q = ' '.join(sys.argv[1:])
    else:
        q = "Tell me something"

    # call twice (wasteful)
    setup_index_and_chat()
    setup_index_and_chat_again()

    result = main_flow(q, output_file='chat_response')
    print('Final result (raw):', result)

    # unreachable dead code example but syntactically valid
    if False:
        print('This will never run')

# TODO: add more features later
# FIXME: this file is intentionally broken for testing
