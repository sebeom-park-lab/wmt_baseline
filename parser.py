import os
from pathlib import Path
import string
import re
from pickle import dump
from unicodedata import normalize
from collections import Counter

import csv

dirname = "data_2_terminology"
newDirname = "data_2_terminology_new2"
filenames = ['train.tsv']


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


def clean_dataset(lines):

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


def remove_voca(newfilename, lines):

    #print("Eng voca size : " + str(len(eng_vocab)))
    count_lines = 0
    for index, line in enumerate(lines):

        lines[index][0] = update_dataset(line[0], eng_vocab)
        lines[index][1] = update_dataset(line[1], fra_vocab)

        
        count_lines = count_lines+1

    print("After removing lines : " + str(count_lines))
    return lines

def write_tsv_file(newfilename, lines):
    
    with open(newfilename, 'w') as out_file:
        tsv_writer = csv.writer(out_file, delimiter='\t')
        for line in lines :
            tsv_writer.writerow([line[0], line[1]])

def save_clean_sentences(sentences, filename):
    dump(sentences, open(filename, 'wb', encoding='UTF8'))
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


def tagging(avail_lines) : 

    filename = "./terminologies/terminologies.fr.txt"
    lines = [line.rstrip('\n').split('\t')
             for line in open(filename, 'r', encoding='UTF8').readlines()]

    tmp_dict = {}
    for line in lines : 
        en_term = line[3]
        fr_term = line[4]
        tmp_dict[en_term] = french_lemm(fr_term)

    print(str(len(tmp_dict)))


    for eng_term, fra_term in tmp_dict.items() :
        re_en = re.compile('(?!> )%s(?! <)'%eng_term, re.I)
        re_fr = re.compile('(?!> )%s(?! <)'%fra_term, re.I)
        for idx, lines in enumerate(avail_lines) :
            en_ = lines[0]
            en_line2 = re_en.sub('<start> %s <end> '%en_term,en_)
            if en_line2 != en_ :
                avail_lines[idx][0] = en_line2

            fr_ = lines[1]
            fr_line2 = fr_
            try :
                m_ = re_fr.search(fr_)
                fr_line2 = re_fr.sub('<start> %s <end> '%m_.group(), fr_)
            except :
                pass
            if fr_line2 != fr_ :
                avail_lines[idx][1] = fr_line2
    

    return avail_lines
    
def french_lemm(term):
    stt = term.split(" ")
    n_stt = ""
    for word in stt:
        if word.endswith("es"):
            word = word[:-2] +".{,2}"
        elif word.endswith("s"):
            word = word[:-1]+ "."
        elif word.endswith("er"):
            word = word[:-2]+".{,4}"
        n_stt += word+" "
    if n_stt.endswith(" "):
        return n_stt[:-1]
    return n_stt

def remove_big_diff(lines):
    
    newLines = []
    for line in lines :
        eng_line = line[0]
        fra_line = line[1]
        len_diff = len(eng_line) - len(fra_line)
        boundary = len(fra_line)
        if(len_diff > boundary):
            continue
        newLines.append(line)
    return newLines


for filename in filenames :

    eng_counter = Counter()
    fra_counter = Counter()
    tmp_filename = os.path.join(dirname, filename)


    lines = [line.rstrip('\n').split('\t')
                for line in open(tmp_filename, 'r',encoding='UTF8').readlines()]

    lines = clean_dataset(lines)
    lines = tagging(lines)

    print("Before removing fault string " + str(len(lines)))
    #print("ENG token before : " + str(len(eng_counter)))
    #print("FRA token before : " + str(len(fra_counter)))
    #eng_vocab=trim_vocab(eng_counter,2)
    #fra_vocab=trim_vocab(fra_counter,2)

    newfilename = os.path.join(newDirname, filename)
    if(not os.path.isdir(newDirname)) :
        os.makedirs(newDirname)

    #lines = remove_voca(newfilename, lines)
    if("train" in tmp_filename):
        lines = remove_big_diff(lines)

    print("After removing fault string " + str(len(lines)))
    write_tsv_file(newfilename,lines)

#print("ENG token after : " + str(len(eng_vocab)))
#print("Fra token after : " + str(len(fra_vocab)))

