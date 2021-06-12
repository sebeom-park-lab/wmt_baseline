import os
from pathlib import Path
import string
import re
from pickle import dump
from unicodedata import normalize
from collections import Counter

import csv

dirname = "data_2_terminology"
newDirname = "DATASET_NO_REMOVE_NAME_WITH_TAGGING3"
filenames = ['train.tsv', 'dev.tsv', 'test.tsv']





def to_sentences(doc):
    return doc.strip().split('\n')


def clean_lines(line):
    line = re.sub('[-=+,#/\:^$.@*]', '', line)
    #line = re.sub(pattern, '', line)
    #line = re.sub('#.+;','',line)    # remove # name ..... until last ,

    #re_print = re.compile('[^%s]' % re.escape(string.printable))
    # prepare translation table for removing punctuation
    #table = str.maketrans('', '', string.punctuation)

    # normalize unicode characters
    #line = normalize('NFD', line).encode('ascii', 'ignore')
    #line = line.decode('UTF-8')
    #line = line.lower()

    # tokenize on white space
    #line = line.split()
    # convert to lower case
    #line = [word.lower() for word in line]
    # remove punctuation from each token
    #line = [word.translate(table) for word in line]
    # remove non-printable chars form each token
    #line = [re_print.sub('', w) for w in line]
    # store as string
    return line
    #return (' '.join(line))


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

def newTagging(avail_lines) : 
    
    filename = "./terminologies/terminologies.fr.txt"
    lines = [line.rstrip('\n').split('\t')
             for line in open(filename, 'r', encoding='UTF8').readlines()]

    tmp_dict = {}
    en_term_dict = {}
    fra_term_dict = {}
    for line in lines : 
        en_term = line[3]
        fr_term = line[4]
        en_term_dict[en_term] = en_term
        fra_term_dict[fr_term] = fr_term
        
        #tmp_dict[en_term] = fr_term

    #print(str(len(tmp_dict)))
    
    for idx, index in enumerate(avail_lines):
        eng = line[0]
        fra = line[1]
        for en_term in en_term_dict.keys() :
            print(en_term)
            if(en_term in eng):
                avail_lines[idx][0] =  eng.replace(eng_term," <start> " + en_term + "<end>")

        for fra_term in fra_term_dict.keys() :
            if(fra_term in fra):
                avail_lines[idx][1] =  fra.replace(fra_term," <start> " + fra_term + "<end>")
        
    return avail_lines


def tagging(avail_lines) : 

    filename = "./terminologies/terminologies.fr.txt"
    lines = [line.rstrip('\n').split('\t')
             for line in open(filename, 'r', encoding='UTF8').readlines()]

    tmp_dict = {}
    for line in lines : 
        en_term = line[3]
        fr_term = line[4]
        tmp_dict[en_term] = french_lemm(fr_term)

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
                print(fr_line2)
                print(fra_term)
    

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
    print("Before Removing Big Diff Size: " + str(len(lines)))

    newLines = []
    for line in lines :
        eng_line = line[0]
        fra_line = line[1]
        len_diff = len(eng_line) - len(fra_line)
        boundary = len(fra_line) 
        if(len_diff > boundary):
            continue
        newLines.append(line)
    print("AFter Removing Big Diff Size: " + str(len(newLines)))
    return newLines



def divide_line(lines):

    print("Before Divided Line Size: " + str(len(lines)))
    newLines = []
    count = 0
    split_count = 0
    for line in lines :    
        #print(line[0] + " / " + line[1])
        eng = line[0]
        fra = line[1]
        expression = "[.?!]\s+"
        divided_eng = re.split(expression,str(eng))
        divided_fra = re.split(expression,str(fra))

        final_eng = []
        for sentence_eng in divided_eng:
            if(len(sentence_eng) > 10 or len(final_eng) == 0):
                final_eng.append(sentence_eng)
            else:
                final_eng[-1] = final_eng[-1] + "." + sentence_eng
        final_fra = []
        for sentence_fra in divided_fra:
            if(len(sentence_fra) > 10 or len(final_fra) == 0):
                final_fra.append(sentence_fra)
            else:
                final_fra[-1] = final_fra[-1] + "." + sentence_fra
        if(len(final_eng) == len(final_fra)):
            split_count = split_count+len(final_eng)
            for tmp_eng, tmp_fra in zip(final_eng, final_fra) :
                #print(tmp_eng)
                #print(tmp_fra)
                newLines.append([tmp_eng,tmp_fra])
        else:
            count = count+1
            newLines.append(line)


    print("Split Count : " + str(split_count))
    print("Original Count : " +str(count)) 
#    print("Skip Count : " + str(count))
#    print("Added Count : " + str(addCount))
#    print("Not Same Count : " + str(notSameCount))

    print("After Divided Line Size: " + str(len(newLines)))
    return newLines


if __name__ == "__main__" :

    for filename in filenames :

        eng_counter = Counter()
        fra_counter = Counter()
        tmp_filename = os.path.join(dirname, filename)

        print(filename)
        lines = [line.rstrip('\n').split('\t')
                    for line in open(tmp_filename, 'r',encoding='UTF8').readlines()]

        lines = clean_dataset(lines)
        #if("train" in tmp_filename):
        lines = remove_big_diff(lines)

        lines = divide_line(lines)
        lines = newTagging(lines)


        newfilename = os.path.join(newDirname, filename)
        if(not os.path.isdir(newDirname)) :
            os.makedirs(newDirname)

        #lines = remove_voca(newfilename, lines)

        write_tsv_file(newfilename,lines)

