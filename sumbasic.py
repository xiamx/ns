#!/usr/bin/env python
# -*- coding: utf-8 -*-


from operator import itemgetter
from nltk.tokenize import sent_tokenize, word_tokenize
import sys
import argparse
import itertools
import nltk
import os
from os.path import dirname, join, realpath
dir_path = dirname(realpath(__file__))
nltk.data.path = [join(dir_path, 'nltk_data')]
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from functools import reduce

wordnet_lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

nltk.data.path.append('./nltk_data/')

# helper methods that apply preprocessing on list of strings

def preprocess(tokens):
    return lemmatize(remove_stopwords(lowercase((tokens))))

def lowercase(tokens):
    return [t.lower() for t in tokens]

def lemmatize(tokens):
    return [wordnet_lemmatizer.lemmatize(t) for t in tokens]

def remove_stopwords(tokens):
    return [t for t in tokens if t.lower() not in stop_words]

def handle_unicode(lines):
    return [l.decode("utf-8") for l in lines]

def flatten(nestedList):
    return list(itertools.chain(*nestedList))

def to_sents(lines):
    return flatten([sent_tokenize(line) for line in lines])

def to_tokens(sents):
    return flatten([word_tokenize(sent) for sent in sents])

def compact(lines):
    """
    remove empty lines
    """
    return [x for x in lines if x and not x.isspace()]

def strip(lines):
    """
    Strip whitespace from input lines
    """
    return [x.strip() for x in lines]

def leading(lines, word_limit):
    sents = to_sents(lines)
    summary = ""
    while len(word_tokenize(summary)) < word_limit:
        summary += " " + sents.pop(0)

# main methods

def orig(lines, word_limit):
    return sum_basic(lines, word_limit, True)
    
def simplified(lines, word_limit):
    return sum_basic(lines, word_limit, False)

def sum_basic(lines, word_limit, update_non_redundency=True):
    def weight(sents, distribution):
        def _weight_sent(sent):
            tokens = preprocess(word_tokenize(sent))
            return reduce(lambda x,y: x+y, [distribution.get(x) for x in tokens]) / len(tokens)
            
        return [_weight_sent(sent) for sent in sents]
    
    def probability_distribution(tokens):
        N = len(tokens)
        distinct_words = set(tokens)
        
        probabilities = [tokens.count(w) / N for w in distinct_words]
        return dict(list(zip(distinct_words, probabilities)))
    
    sents = to_sents(lines)
    tokens = to_tokens(sents)
    tokens = preprocess(tokens)
    
    pd = probability_distribution(tokens)
    
    summary = "" 
    
    while len(word_tokenize(summary)) < word_limit:
        weights = weight(sents, pd)
        highest_weight_sentence = max(list(zip(sents, weights)), key=itemgetter(1))[0]
        summary += " " + highest_weight_sentence
        if update_non_redundency:
            for token in preprocess(word_tokenize(highest_weight_sentence)):
                pd[token] = pd[token] * pd[token]
        else:
            sents.remove(highest_weight_sentence)
            
   
    return summary 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A4 SumBasic")
    parser.add_argument("method", choices=[
        "orig", "simplified", "leading"
        ], help="summerizor method")
    parser.add_argument('infiles', nargs='*', type=argparse.FileType('r'),
        default=[sys.stdin])
    args = parser.parse_args()
    nestedlines = [f.readlines() for f in args.infiles]
    lines = compact(strip(handle_unicode(flatten(nestedlines))))
    
    if args.method == "orig":
        print(orig(lines, 100))
    elif args.method == "simplified":
        print(simplified(lines, 100))
    elif args.method == "leading":
        print(simplified(lines, 100))
    
    