#! /usr/bin/python

import sys
import weight_vector

# Code I wrote for Coursera NLP class.  Uses Global Linear Model
# [aka Conditional Random Field] to tag sentences.  The programs uses the
# veterbi algorithm to compute the tagging that has the best score under the
# model.

# I am still learning python so any suggestions are welcome :)

# Including WeightVector code for reference.
# class WeightVector(object):
#
#     def __init__(self):
#         self.weights = {}
#         return
#
#     def __str__(self):
#         return repr(self.weights)
#
#     def value(self, key):
#         ret = 0
#         if key in self.weights:
#             ret = self.weights[key]
#
#         return ret
#
# class WeightVectorFromFile(WeightVector):
#
#     def __init__(self, filename):
#         super(WeightVectorFromFile, self).__init__()
#
#         with open(filename) as f:
#             training_data = f.readlines()
#
#         for l in training_data:
#             [rule, score] = l.strip().split(" ")
#             self.weights[rule] = float(score)

class Table(object):
    def key(self, k, u, s):
        return "%d,%s,%s" % (k, u, s)

    def __init__(self):
        self.table = {}

class PiTable(Table):

    def __init__(self):
        super(PiTable, self).__init__()
        self.table[self.key(0, '*', '*')] = 0

    def set_value(self, k, u, s, value):
        self.table[self.key(k, u, s)] = value

    def get_value(self, k, u, s):
        return self.table[self.key(k, u, s)]

class BpTable(Table):

    def __init__(self):
        super(BpTable, self).__init__()

    def set_tag(self, k, u, s, tag):
        self.table[self.key(k, u, s)] = tag

    def get_tag(self, k, u, s):
        return self.table[self.key(k, u, s)]

class GVector(object):

    def trigram_key(self, t2, t1, t):
        return "TRIGRAM:%s:%s:%s" % (t2, t1, t)

    def tag_key(self, x, i, t):
        return "TAG:%s:%s" % (x[i-1], t)

    def __init__(self, t2, t1, x, i, t):
        self.h = {}

        self.h[self.trigram_key(t2, t1, t)] = 1
        if i <= len(x):
            self.h[self.tag_key(x, i, t)] = 1

    def dot_product(self, v):
        return sum(v.value(k) * val for k,val in self.h.iteritems())

def viterbi(v, sentence):

    pi = PiTable()
    bp = BpTable()
    k_tags = ["O", "I-GENE"]
    k_one_tags = ["*"]
    k_two_tags = ["*"]
    ret = []

    # Build Pi Table for sentence by saving that max score for different tags
    for k in range(1, len(sentence) + 1):

        for u in k_one_tags:
            for s in k_tags:

                max_pi = -float("inf")

                for t in k_two_tags:

                    g = GVector(t, u, sentence, k, s)
                    dp = g.dot_product(v)

                    score = pi.get_value(k - 1, t, u) + dp

                    if score > max_pi:
                        max_pi = score
                        pi.set_value(k, u, s, score)
                        bp.set_tag(k, u, s, t)

        k_two_tags = k_one_tags
        k_one_tags = k_tags

    score = -float("inf")
    tn = ""
    tn1 = ""

    # now determine which tags[tn, tn1] to use when for going through
    # back-pointer table bp.  I do this by calculating which tags
    # have the best score before STOP.
    for u in k_tags:
        for s in k_tags:
            g  = GVector(u, s, sentence, len(sentence) + 1, "STOP")
            temp_score = pi.get_value(len(sentence), u, s) + g.dot_product(v)

            if temp_score > score:
                tn = s
                tn1 = u
                score = temp_score

    # Now that I have the last 2 tags go through the back pointer table
    # to reconstruct the highest scoring tagging for the sentence.
    labels = [tn, tn1]
    tk1 = tn1
    tk2 = tn
    for i in range(2, len(sentence)):
        k = len(sentence) - i

        l = bp.get_tag(k + 2, tk1, tk2)
        labels.append(l)
        tk2 = tk1
        tk1 = l

    labels.reverse()

    for i in range(len(sentence)):
        ret.append("%s %s" % (sentence[i], labels[i]))

    return ret

def get_sentences_from_file(input_file):

    with open(input_file) as f:
        data = f.readlines()

    ret = []
    temp = []

    # each sentences ends with a newline so just check for length 1 word.
    for word in data:
        if len(word) == 1:
            ret.append(temp)
            temp = []
        else:
            temp.append(word.strip())

    return ret


def usage():
    print """python viterbi_glm.py [tag_file] [input_to_label] > [label_output]
             takes a tag_model file and data to label and outputs data to label.
          """

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    model_file = sys.argv[1]
    input_file = sys.argv[2]

    v = weight_vector.WeightVectorFromFile('f')

    sentences = get_sentences_from_file(input_file)

    out = []
    for s in sentences:
        out.append(viterbi(v, s))

    for words in out:
        for wl in words:
            print wl
        print ""

