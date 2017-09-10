#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import t_params
import json

TRAINING_ITERATIONS = 5
Q_FILE = "q_dump.txt"

def i_l_m_key(i, l, m):
    return "%d,%d,%d" % (i, l, m)

def j_i_l_m_key(j, i, l, m):
    return "%d|%d,%d,%d" % (j, i, l, m)

def to_i_l_m_key(j_i_l_m_k):
    return j_i_l_m_k.split("|")[1]

class Counts(object):

    def __init__(self):
        self.count_i_l_m = {}
        self.count_j_i_l_m = {}

    def counts(self):
        for k in self.count_j_i_l_m.keys():
            i_l_m_k = to_i_l_m_key(k)
            yield [k, self.count_j_i_l_m[k] / self.count_i_l_m[i_l_m_k]]

    def i_l_m_count(self, i, l, m):

        ret = 0
        k = i_l_m_key(i, l, m)

        if k in self.count_i_l_m:
            ret = self.count_i_l_m[k]

        return ret

    def j_i_l_m_count(self, j, i, l, m):
        ret = 0
        k = j_i_l_m_key(j, i, l, m)

        if k in self.count_j_i_l_m:
            ret = self.count_j_i_l_m[k]

        return ret

    def set_i_l_m_count(self, i, l, m, value):
        self.count_i_l_m[i_l_m_key(i, l, m)] = value
        return

    def set_j_i_l_m_count(self, j, i, l, m, value):
        self.count_j_i_l_m[j_i_l_m_key(j, i, l, m)] = value
        return

class ModelTwo(t_params.TParamsTable):

    def __init__(self):

        # init t-table from file.
        super(ModelTwo, self).__init__()
        self.read_from_file(t_params.DUMP_FILE)

        self.q = {}

        for [e_words, s_words] in self.sentences():
            l = len(e_words)
            m = len(s_words)

            if j_i_l_m_key(0, 0, l, m) in self.q:
                continue

            for i in range(m):
                for j in range(l):
                    self.q[j_i_l_m_key(j, i, l, m)] = (float(1) / (l + 1))

    def delta(self, j, i, l, m, e_words, s_word, e_word):

        q = self.q[j_i_l_m_key(j, i, l, m)]
        t = self.t_f_e(s_word, e_word)

        sum_qtfe = 0
        for jj in range(len(e_words)):
            q_key = j_i_l_m_key(jj, i, l, m)
            sum_qtfe += (self.t_f_e(s_word, e_words[jj]) * self.q[q_key])

        return (q * t)/sum_qtfe

    def update_q_from_counts(self, c):

        for [key, value] in c.counts():
            self.q[key] = value

    def train(self, iterations):

        for it in range(iterations):
            c = Counts()

            iiii = 0
            jjjj = 0
            inc = (len(self.en_sentences) + 99) / 100
            for [e_words, s_words] in self.sentences():
                iiii += 1
                if iiii % inc == 0:
                    jjjj += 1
                    print "%d percent done" % jjjj

                m = len(s_words)
                l = len(e_words)
                for i in range(m):
                    for j in range(l):

                        d = self.delta(j, i, l, m, e_words, s_words[i], e_words[j])
                        c.set_i_l_m_count(i, l, m, c.i_l_m_count(i, l, m) + d)
                        c.set_j_i_l_m_count(j, i, l, m, c.j_i_l_m_count(j, i, l, m) + d)

            self.update_q_from_counts(c)

        return

    def compute_alignments(self, sp_file, eng_file):
        ret = []
        sentence_index = 1
        for [e_words, s_words] in self.get_words(eng_file, sp_file):

            i = 0
            m = len(s_words)
            l = len(e_words)

            for s_w in s_words:
                a = -1
                a_max = 0
                j = 0

                for e_w in e_words:
                    score = self.q[j_i_l_m_key(j, i, l, m)] * self.t_f_e(s_w, e_w)
                    if score > a_max:
                        a_max = score
                        a = j + 1
                    j += 1

                ret.append("%d %d %d" % (sentence_index, a, i+1))
                i += 1

            sentence_index += 1

        return ret

    def q_to_file(self, fname):

        s = json.dumps(self.q)

        with open(fname, 'w') as f:
            f.write(s)

        return

    def q_from_file(self, fname):

        with open(fname) as f:
            s = f.readline()

        self.q = json.loads(s)

        return

def usage():
    print """python model2.py  [sp_file] [eng_file] > alignments
             runs IBM Model 2 alignments on files and outputs alignments.
          """

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    sp_file = sys.argv[1]
    eng_file = sys.argv[2]

    m2 = ModelTwo()
    # m2.train(TRAINING_ITERATIONS)

   # m2.q_to_file(Q_FILE)
    m2.q_from_file(Q_FILE)

    alignments = m2.compute_alignments(sp_file, eng_file)

    for l in alignments:
        print l