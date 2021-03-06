#!/usr/bin/env python

# -*- coding:utf-8 -*-

# LDA: generic LDA implementation using gensim

import logging
from gensim import corpora, models, similarities
import nltk
import argparse
import csv


class LDA():
    def __init__(self, __logLevel, __infile, __topics):
        self.log = logging.getLogger('LDA')
        self.log.setLevel(__logLevel)
        self.infile = __infile
        self.topics = __topics
        self.documents = []

        # 1. Load text file
        self.readFile()
        self.log.debug(self.documents)

        # 2. Compute LDA
        self.computeLDA()

        # 3. Serialize Turtle

    def readFile(self):
        with open(self.infile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quotechar='"')
            next(reader, None)  # skip headers
            for row in reader:
                self.documents.append(unicode(row[1], 'utf-8'))

    def computeLDA(self):
        utf_stopwords = ['\u0xc2']
        tokenizer = nltk.tokenize.RegexpTokenizer('\(.*\)|[\s\.\,\%\:\$]+', gaps=True)
        texts = [[word for word in tokenizer.tokenize(document.lower())
                  if word not in nltk.corpus.stopwords.words('english')] for document in self.documents]
        self.log.debug(texts)

        # remove words that appear only once
        all_tokens = sum(texts, [])
        tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        texts = [[word for word in text if word not in tokens_once] for text in texts]
        self.log.debug(texts)

        self.dictionary = corpora.Dictionary(texts)
        self.dictionary.save('/tmp/deerwester.dict')
        self.log.debug(self.dictionary)

        self.corpus = [self.dictionary.doc2bow(text) for text in texts]
        corpora.MmCorpus.serialize('/tmp/deerwester.mm', self.corpus)
        self.log.debug(self.corpus)

        self.tfidf = models.TfidfModel(self.corpus)
        corpus_tfidf = self.tfidf[self.corpus]
        self.log.debug(self.tfidf)

        lda = models.ldamodel.LdaModel(corpus=self.corpus, id2word=self.dictionary,
                                       num_topics=self.topics, update_every=1, chunksize=10000, passes=1)
        lda.print_topics(10)


if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Simple LDA using gensim")
    parser.add_argument('--infile', '-i',
                        help="Read corpus from file",
                        required=True)
    parser.add_argument('--verbose', '-v',
                        help="Be verbose -- debug logging level",
                        required=False,
                        action='store_true')
    parser.add_argument('--topics', '-t',
                        help="Number of topics",
                        required=True)
    args = parser.parse_args()

    # Logging
    logLevel = logging.INFO
    if args.verbose:
        logLevel = logging.DEBUG
    logging.basicConfig(level=logLevel)
    logging.info('Initializing...')

    # Instance
    lda = LDA(logLevel, args.infile, int(args.topics))

    logging.info('Done.')
