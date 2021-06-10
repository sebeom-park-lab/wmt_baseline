import os
from pathlib import Path
import string
import re
from pickle import dump
from unicodedata import normalize
from collections import Counter

import csv

dirname = "data_2_terminology"
filenames = ['train.tsv', 'test.tsv', 'dev.tsv']


def load_doc():
    # open the file as read only
    file = open(filename, mode='rt', encoding='utf-8')
    # read all text
    text = file.read()
    # close the file
    file.close()
    return text


def to_sentences(doc):
    return doc.strip().split('\n')


def clean_lines(line):
    re_print = re.compile('[^%s]' % re.escape(string.printable))
    # prepare translation table for removing punctuation
    table = str.maketrans('', '', string.punctuation)

    # normalize unicode characters
    line = normalize('NFD', line).encode('ascii', 'ignore')
    line = line.decode('UTF-8')

    # tokenize on white space
    line = line.split()
    # convert to lower case
    line = [word.lower() for word in line]
    # remove punctuation from each token
    line = [word.translate(table) for word in line]
    # remove non-printable chars form each token
    line = [re_print.sub('', w) for w in line]
    # store as string
    return (' '.join(line))


def clean_dataset(filename):

    lines = [line.rstrip('\n').split('\t')
             for line in open(filename, 'r').readlines()]
    print("Original dataset lines : " + str(len(lines)))
    for index, line in enumerate(lines):
        eng_str = clean_lines(line[0])
        fra_str = clean_lines(line[1])

        lines[index][0] = eng_str
        lines[index][1] = fra_str

        eng_tokens = eng_str.split()
        eng_counter.update(eng_tokens)

        
        fra_tokens = fra_str.split()
        fra_counter.update(fra_tokens)
    return lines


def remove_voca(filename, lines):
    basename = os.path.basename(filename)
    newName = os.path.splitext(basename)[0] + "_new.tsv"
    newPath = os.path.join(dirname, newName)

    #print("Eng voca size : " + str(len(eng_vocab)))

    with open(newPath, 'w') as out_file:
        count_lines = 0
        tsv_writer = csv.writer(out_file, delimiter='\t')
        for index, line in enumerate(lines):

            converted_eng = update_dataset(line[0], eng_vocab)
            converted_fra = update_dataset(line[1], fra_vocab)

            len_diff = len(converted_eng) - len(converted_fra)
            if(len_diff > (len(converted_fra) / 2)):
                continue
            tsv_writer.writerow([converted_eng, converted_fra])
            count_lines = count_lines+1


def load_clean_sentences(filename):
    return load(open(filename, 'rb'))

def save_clean_sentences(sentences, filename):
    dump(sentences, open(filename, 'wb'))
    print('Saved: %s' % filename)



def to_vocab(lines):
    vocab = Counter()
    for line in lines:
        tokens = line.split()
        vocab.update(tokens)
    return vocab

def update_dataset(line, vocab):

    new_tokens = list()
    for token in line.split():
        if token in vocab:
            new_tokens.append(token)
        else:
            new_tokens.append('<unk>')
    new_line = ' '.join(new_tokens)

    return new_line


def trim_vocab(vocab, min_occurance):
    newTokens = []
    for key, count in vocab.items():
        if(count >= min_occurance):
            newTokens.append(key)
    return set(newTokens)




for filename in filenames :
    eng_counter = Counter()
    fra_counter = Counter()
    filename = os.path.join(dirname, filenames[0])
    lines = clean_dataset(filename)
    eng_vocab=trim_vocab(eng_counter,2)
    fra_vocab=trim_vocab(fra_counter,2)
    remove_voca(filename, lines)
