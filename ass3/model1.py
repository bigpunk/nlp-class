#! /usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import sys
import t_params

class Counts(object):

    def __init__(self):
        self.count_table_e = {}
        self.count_table_e_s = {}

    def e_count(self, e_word):
        ret = 0

        if e_word in self.count_table_e:
            ret = self.count_table_e[e_word]

        return float(ret)

    def e_s_count(self, e_word, s_word):
        ret = 0
        key = "%s_$$_%s" % (e_word, s_word)

        if key in self.count_table_e_s:
            ret = self.count_table_e_s[key]

        return float(ret)

    def set_e_count(self, e_word, value):
        self.count_table_e[e_word] = value
        return

    def set_e_s_count(self, e_word, s_word, value):
        key = "%s_$$_%s" % (e_word, s_word)
        self.count_table_e_s[key] = value
        return

class ModelOne(t_params.TParamsTable):

    def __init__(self):
        super(ModelOne, self).__init__()

    def update_t_from_counts(self, counts):

        for e_word in self.t.keys():
            for s_word in self.t[e_word].keys():

                val = counts.e_s_count(e_word, s_word) / counts.e_count(e_word)

                self.set_t_f_e(s_word, e_word, val)

    def train_model_one(self, iterations):

        for it in range(iterations):
            c = Counts()

            for [e_words, s_words] in self.sentences():
                for s_word in s_words:
                    for e_word in e_words:

                        d = self.delta(e_words, s_word, e_word)

                        c.set_e_count(e_word, c.e_count(e_word) + d)
                        c.set_e_s_count(e_word, s_word, c.e_s_count(e_word,s_word) + d)

            self.update_t_from_counts(c)

    def delta(self, e_words, s_word, e_word):

        tfe = self.t_f_e(s_word, e_word)

        sum_tfe = 0
        for w in e_words:
            sum_tfe += self.t_f_e(s_word, w)

        return tfe/sum_tfe

    def determine_alignments(self, e_file, s_file):

        ret = []

        sentence_index = 1
        for [e_words, s_words] in self.get_words(e_file, s_file):

            s_word_index = 1
            for s_w in s_words:
                a = -1
                a_max = 0
                j = 1

                for e_w in e_words:
                    score = self.t_f_e(s_w, e_w)
                    if score > a_max:
                        a_max = score
                        a = j
                    j += 1

                ret.append("%d %d %d" % (sentence_index, a, s_word_index))
                s_word_index += 1

            sentence_index += 1

        return ret

def usage():
    print """python model1.py [iterations] [outfile]
             computes alignments training model 1 over iterations and
              writes the output to outfile """

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    #iterations = int(sys.argv[1])
    #outfile = sys.argv[2]

    spanish_file = sys.argv[1]
    eng_file = sys.argv[2]

    m1 = ModelOne()

    #m1.train_model_one(iterations)
    m1.read_from_file('dump_file.txt')

    alignments = m1.determine_alignments(eng_file, spanish_file)

    for a in alignments:
        print a



