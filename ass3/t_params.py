#! /usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import json
import sys

EN_CORPUS_FILENAME = 'corpus.en'
ES_CORPUS_FILENAME = 'corpus.es'
DUMP_FILE = "dump_file.txt"

class TParamsTable(object):

    def sentences(self):

        for i in range(len(self.en_sentences)):
            e_words = self.en_sentences[i].split(" ")
            s_words = self.es_sentences[i].split(" ")

            if len(e_words) == 1 or len(s_words) == 1:
                continue

            yield [e_words, s_words]

    def set_t_f_e(self, es_word, en_word, value):

        if en_word not in self.t:
            self.t[en_word] = {}

        self.t[en_word][es_word] = value

    def t_f_e(self, es_word, en_word):
        return self.t[en_word][es_word]

    def __init__(self):

        with codecs.open(EN_CORPUS_FILENAME, "r", "utf-8") as f:
            self.en_sentences = f.readlines()

        with codecs.open(ES_CORPUS_FILENAME, "r", "utf-8") as f:
            self.es_sentences = f.readlines()

        self.t = {}

        eng_words = {}

        # filter out sentences that are just newlines.
        #len_one_test = lambda x: len(x) > 1
        #self.en_sentences = filter(len_one_test, self.en_sentences)
        #self.es_sentences = filter(len_one_test, self.es_sentences)

        for [e_words, s_words] in self.sentences():
            for e_w in e_words:

                if e_w not in eng_words:
                    eng_words[e_w] = {}

                for s_w in s_words:
                    eng_words[e_w][s_w] = 1

        for e_word in eng_words.keys():
            total_count = len(eng_words[e_word].keys())

            for s_word in eng_words[e_word].keys():
                self.set_t_f_e(s_word, e_word, float(1)/total_count)

    def __str__(self):
        return repr(unicode(self.t))

    def rare_eng_words(self, num):

        print "Rare English words:"
        for e in self.t.keys():
            if len(self.t[e].keys()) < num:
                print e

    def dump_to_file(self, fname):

        s = json.dumps(self.t)

        with open(fname, 'w') as f:
            f.write(s)

        return

    def read_from_file(self, fname):

        with open(fname) as f:
            s = f.readline()

        self.t = json.loads(s)

        return

    def get_words(self, e_file, s_file):

        with codecs.open(e_file, "r", "utf-8") as f:
            eng_lines = f.readlines()

        with codecs.open(s_file, "r", "utf-8") as f:
            span_lines = f.readlines()

        for i in range(len(eng_lines)):
            e_words = eng_lines[i].split(" ")
            s_words = span_lines[i].split(" ")

            yield [e_words, s_words]

def usage():
    print """python t_params builds t_parms table from corpus.en and corpus.es
          """

if __name__ == "__main__":

    if len(sys.argv) != 1:
        usage()
        sys.exit(2)

    t_values = TParamsTable()

    t_values.dump_to_file('dump_file.txt')

    t_values.read_from_file('dump_file.txt')






