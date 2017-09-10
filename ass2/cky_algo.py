#! /usr/bin/python

import json
import math
import sys
import tree_utils

class BpTable(object):

    def __init__(self, words):
        self.words = words
        self.table = {}

    def add_bp(self, i, j, x, rule, s):
        key = "%d %d %s" % (i, j, x)
        value = [rule, s]
        self.table[key] = value

    def get_value(self, start, end, sym):
        key = "%d %d %s" % (start, end, sym)
        return self.table[key]

    def __str__(self):
        s = ""
        for k,v in self.table.iteritems():
            s += ("%s : %s" % (k, v))

        return "{ " + s + " }"

    def build_parse_tree(self, nt, start, end):

        if start == end:
            return [nt, self.words[start - 1]]

        [rule, split] = self.get_value(start, end, nt)
        nonterms = rule.split(" ")

        node = nonterms[0]
        left = self.build_parse_tree(nonterms[1], start, split)
        right = self.build_parse_tree(nonterms[2], split + 1, end)

        return [node, left, right]


class PiTable(object):

    def __init__(self, unary_counts, total_rule_counts, words):

        self.table = {}

        for i in range(len(words)):
            w = words[i]

            # use _RARE_ if we didn't have enough training examples for w
            if w not in unary_counts:
                w = '_RARE_'

            for rule in unary_counts[w].iterkeys():
                key = "%d %d %s" % (i + 1, i + 1, rule)
                value = unary_counts[w][rule] / total_rule_counts[rule]
                self.table[key] = -math.log(value)
                assert(self.table[key] >= 0.0)

    def __str__(self):

        s = ""
        for k,v in self.table.iteritems():
            s += ("%s : %s" % (k, v))

        return "{ " + s + " }"

    def set_value(self, i, j, rule, value):

        key = "%d %d %s" % (i, j, rule)
        self.table[key] = value

    def get_value(self, i, j, rule):

        key = "%d %d %s" % (i, j, rule)

        if key in self.table:
            assert(self.table[key] >= 0.0)
            return self.table[key]
        else:
            return float("inf")

class CKY_Parser(object):

    def __init__(self, training_file):

        tree_utils.run_count_cfg_freq(training_file)
        self.unary_counts = tree_utils.get_unary_counts()

        self.binary_rule_counts = tree_utils.get_binary_counts()
        self.total_rule_counts = tree_utils.get_nonterminal_counts()

    def rule_log_prob(self, rule):

        x = rule.split(" ")[0]
        prob = self.binary_rule_counts[rule] / self.total_rule_counts[x]

        return -math.log(prob)


    def parse(self, sentence):
        ret = []
        words = sentence.split(" ")

        pi = PiTable(self.unary_counts, self.total_rule_counts, words)
        bp = BpTable(words)


        nonterminals = tree_utils.nonterminal_list(self.total_rule_counts)
        rules = tree_utils.rule_list(self.binary_rule_counts)

        for l in range(1, len(words)):
            for i in range(1, len(words) - l + 1):
                for x in nonterminals:

                    max_pi = float("inf")
                    j = i + l
                    for rule in rules:
                        if tree_utils.rule_starts_with(x, rule):
                            for s in range(i, j):
                                rprob = self.rule_log_prob(rule)
                                assert(rprob >= 0.0)
                                y = rule.split(" ")[1]
                                z = rule.split(" ")[2]
                                temp_pi = rprob + pi.get_value(i, s, y) + pi.get_value(s + 1, j, z)
                                assert(temp_pi >= 0.0)
                                if temp_pi < max_pi:
                                    max_pi = temp_pi
                                    bp.add_bp(i, j, x, rule, s)
                                    pi.set_value(i, j, x, max_pi)

        pt = bp.build_parse_tree("SBARQ", 1, len(words))

        return pt

def usage():
    print """python cky_alog.py [rare_words_training_file] [sentence_file] > parse_trees
             Takes training file with infrequent words replaced with "_RARE_"
             and uses it to parse the sentences with the cky algorithm"""

if __name__ == "__main__":

    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    training_file = sys.argv[1]
    sentence_file = sys.argv[2]

    parser = CKY_Parser(training_file)

    with open(sentence_file) as f:
        sentences = f.readlines()

    parse_trees = []

    for s in sentences:
        parse_trees.append(parser.parse(s.strip()))

    for t in parse_trees:
        print json.dumps(t)
